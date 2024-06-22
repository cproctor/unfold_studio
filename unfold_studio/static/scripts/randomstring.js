define({
    generate: function(i) {
        var chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        return Array(i).join().split(',').map(function() { 
            return chars.charAt(Math.floor(Math.random() * chars.length)); 
        }).join('');
    }
})
