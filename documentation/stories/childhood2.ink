VAR has_slurpee = false

It's 11pm on a Friday night, sometime in ninth grade. Two friends are sleeping over. 
-> bedroom    

=== bedroom ===
You are in your bedroom. 
+ Go outside 
    -> street

=== street ===
You are on a quiet, moonlit street. 
+ Go back inside.
    -> bedroom
+ Walk to the end of the street.
    -> path

=== path ===
You are on a dark path. 
+ Go back onto the street.
    -> street
+ Walk to 7-11. 
-> seven_eleven
+ Walk to the playground.
    -> playground

=== seven_eleven ===
You walk to 7-11. The garishly-bright interior feels incongruous 
with the peaceful night. 
+ Buy a Slurpee.
   -> buy_slurpee 
+ Walk to the playground.
    -> playground
+ Walk back to the path.
    -> path

=== buy_slurpee ===
~ has_slurpee = true
Your sleepy eyes are mesmerized by the spinning slush in the Slurpee machine. 
You slowly fill the cup with cherry slush, then switch to root beer 
all the way to the top of the rounded lid. 
+ Walk to the playground.
    -> playground
+ Walk back to the path.
    -> path

=== playground ===
You sit on the swings of a deserted playground.
+ Walk to 7-11.
    -> seven_eleven
+ Walk back to the path.
    -> path

