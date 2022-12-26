function validateForm() {
    var x = document.forms["register"]["password"].value;
    var y = document.forms["register"]["resetpw"].value;
    if (x !== y) {
        alert("You need to check the password!");
        return false;
    }
    }
