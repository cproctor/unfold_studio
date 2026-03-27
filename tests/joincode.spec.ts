import { test, expect } from '@playwright/test';

test('verify join logic via requests', async ({ page, request }) => {
  // 1. SETUP: Define your base URL and Group ID
  // Ensure this matches your local server and an existing group
  const BASE_URL = 'http://127.0.0.1:8000';
  const groupId = 1; 

  // 2. AUTHENTICATION: Log in via the UI first
  // This automatically attaches session cookies to the 'request' object
  await page.goto(`${BASE_URL}/login/`);
  await page.fill('input[name="username"]', 'teacher_user'); // Replace with real test user
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(`${BASE_URL}/`); // Verify login success

  // 3. GENERATE CODES (POST request)
  // Ensure you added @csrf_exempt to the GenerateCodesView in views.py
  const generateResponse = await request.post(`${BASE_URL}/groups/${groupId}/generate/`, {
    form: { quantity: '1' },
    headers: { 
        'Referer': `${BASE_URL}/groups/${groupId}/invite/`,
        'X-Requested-With': 'XMLHttpRequest' 
    }
  });
  expect(generateResponse.ok()).toBeTruthy();

  // 4. GET THE CODE FROM THE INVITE PAGE
  const invitePageResponse = await request.get(`${BASE_URL}/groups/${groupId}/invite/`);
  const html = await invitePageResponse.text();

  // Scrapes the 5-character code.
  const codeMatch = html.match(/[A-Z0-9]{5}/); 

  // FIX: Use a guard or a fallback string
  const joinCode = codeMatch ? codeMatch[0] : ''; 

  // Verify it's not empty before proceeding
  expect(joinCode, 'Regex failed to find a join code in the HTML').not.toBe('');

  // 5. JOIN THE GROUP
  const joinResponse = await request.get(`${BASE_URL}/groups/${groupId}/join/`, {
    // TypeScript is now happy because joinCode is guaranteed to be a string
    params: { code: joinCode }
  });

  // Verify that the join logic redirected us back to the group detail page
  expect(joinResponse.url()).toContain(`/groups/${groupId}/`);
  
  // 6. VERIFY THE UI UPDATE
  const finalPageResponse = await request.get(`${BASE_URL}/groups/${groupId}/invite/`);
  const finalHtml = await finalPageResponse.text();
  
  // Verify that the username now appears in the table
  // and the placeholder "Student 1" logic has been replaced
  expect(finalHtml).toContain('teacher_user'); 
  expect(finalHtml).not.toContain('Student 1</span>'); 
});