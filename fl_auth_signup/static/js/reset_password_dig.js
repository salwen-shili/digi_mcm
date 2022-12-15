$(document).ready(function () {
  //test password

  $(`#password`).keyup(function (e) {
    showPasswordPopover();
    const password = $("#password").val();
    const errorMessage = checkPassword(password);
    if (errorMessage === false) {
      $(`#password_container `).removeClass("error-input-field");
      $(`#password_helper `).append("");
    } else {
      // buttonInscrire.setAttribute("disabled", "disabled");

      $(`#password_container `).addClass("error-input-field");
      $(`#password_helper span `).text(errorMessage);
    }
    checkStrength(password);
  });

  function checkPassword(value) {
    if (value.length > 0) {
      if (value.length < 8)
        return "Votre mot de passe doit contenir au minimum 8 caractères";
      else return false;
      // else {
      //   const pattern =
      //     /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!/+/='":;(){}[|@$ %^&*-]).{8,}$/;
      //   if (value.match(pattern)) return false;
      //   else
      //     return `Votre mot de passe doit contenir une combinaison de chiffres, caractères spéciaux, lettres majuscules et minuscules!`;
      // }
    } else return "Ce champs est obligatoire!";
  }
  function checkConfirmPassword(value) {
    if (value.length > 0) {
      if (value.length < 8)
        return "Votre mot de passe doit contenir au minimum 8 caractères";
      else return false;
      // else {
      //   const pattern =
      //     /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!/+/='":;(){}[|@$ %^&*-]).{8,}$/;
      //   if (value.match(pattern)) return false;
      //   else
      //     return `Votre mot de passe doit contenir une combinaison de chiffres, caractères spéciaux, lettres majuscules et minuscules!`;
      // }
    } else return "Ce champs est obligatoire!";
  }

  //Validate Address

  $("#password_form").submit(function (e) {
    $(`#confirm_password_container `).removeClass("error-input-field");
    $(`#confirm_password_helper `).append("");
    if (password.value == "" || confirm_password.value == "") {
      e.preventDefault();
      return;
    }
    if (password.value != confirm_password.value) {
   
 
      // buttonInscrire.setAttribute("disabled", "disabled");
      e.preventDefault();
      $(`#confirm_password_container `).addClass("error-input-field");
      $(`#confirm_password_helper span `).text(
        "Les mots de passe ne correspondent pas"
      );
      return;
    }
    const check = document.querySelector(".error-input-field");
    if (check != null) {
      e.preventDefault();
      return;
    } else {
    }
  });
});

let state = false;
let password = document.getElementById("password");
let confirm_password = document.getElementById("confirm_password");
let passwordStrength = document.getElementById("password-strength");
let lowUpperCase = document.querySelector(".low-upper-case i");
let number = document.querySelector(".one-number i");
// let specialChar = document.querySelector('.one-special-char i');
let eightChar = document.querySelector(".eight-character i");
let nivLevel = document.querySelector(".nivLevel");

function checkStrength(password) {
  let strength = 0;

  //If password contains both lower and uppercase characters
  if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) {
    strength += 1;
    lowUpperCase.classList.remove("fa-check");
    lowUpperCase.classList.add("fa-check");
  } else {
    lowUpperCase.classList.add("fa-check");
    lowUpperCase.classList.remove("fa-check");
  }
  //If it has numbers and characters
  if (password.match(/([0-9])/)) {
    strength += 1;

    number.classList.add("fa-check");
  } else {
    number.classList.remove("fa-check");
  }
  //If it has one special character
  // if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) {
  //   strength += 1;

  //   specialChar.classList.add('fa-check');
  // } else {
  //   specialChar.classList.remove('fa-check');
  // }
  //If password is greater than 5
  if (password.length > 7) {
    strength += 1;

    eightChar.classList.add("fa-check");
  } else {
    eightChar.classList.remove("fa-check");
  }

  // If value is less than 2
  if (strength == 0) {
    passwordStrength.classList.remove("progress-bar-warning");
    passwordStrength.classList.remove("progress-bar-success");
    passwordStrength.classList.remove("progress-bar-danger");
    nivLevel.classList.remove("niv-level-1");
    nivLevel.classList.remove("niv-level-2");
    nivLevel.classList.remove("niv-level-3");

    nivLevel.classList.add("niv-level-1");
    nivLevel.innerHTML = "faible";
  }
  if (strength == 1) {
    passwordStrength.classList.remove("progress-bar-warning");
    passwordStrength.classList.remove("progress-bar-success");
    passwordStrength.classList.add("progress-bar-danger");
    passwordStrength.style = "width: 25%";
    nivLevel.innerHTML = "faible";
    nivLevel.classList.add("niv-level-1");
    nivLevel.classList.remove("niv-level-3");
    nivLevel.classList.remove("niv-level-2");
  } else if (strength == 2) {
    passwordStrength.classList.remove("progress-bar-success");
    passwordStrength.classList.remove("progress-bar-danger");
    passwordStrength.classList.add("progress-bar-warning");
    passwordStrength.style = "width: 55%";
    nivLevel.innerHTML = "moyenne";
    nivLevel.classList.add("niv-level-2");
    nivLevel.classList.remove("niv-level-1");
    nivLevel.classList.remove("niv-level-3");
  } else if (strength == 3) {
    passwordStrength.classList.remove("progress-bar-warning");
    passwordStrength.classList.remove("progress-bar-danger");
    passwordStrength.classList.add("progress-bar-success");
    passwordStrength.style = "width: 100%";
    nivLevel.innerHTML = "optimale";
    nivLevel.classList.add("niv-level-3");
    nivLevel.classList.remove("niv-level-1");
    nivLevel.classList.remove("niv-level-2");
  }
}
//Hide password poover
function hidePasswordPopover() {
  const password = $("#password").val();
  if (password.length > 7) {
    document.getElementById("popover-password").classList.add("hide");
  }
}
function showPasswordPopover() {
  document.getElementById("popover-password").classList.remove("hide");
}
