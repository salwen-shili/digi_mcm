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
  let specialChar = document.querySelector('.one-special-char i');
  let eightChar = document.querySelector(".eight-character i");
  let nivLevel = document.querySelector(".nivLevel");
  
  function checkStrength(password) {
    const email = $("#email").val();
    const lastname = $("#lastname").val();
    const firstname = $("#firstname").val();
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
  
    if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) {
      strength += 1;
      specialChar.classList.add("fa-check");
    } else {
      specialChar.classList.remove("fa-check");
    }
  
    //If password is greater than 7
    if (password.length > 7) {
      strength += 1;
      eightChar.classList.add("fa-check");
    } else {
      eightChar.classList.remove("fa-check");
    }
  
    //Compare password similarity with Name and lastname
    // Jaro-Winkler Algorithm for similarity comparison
    if (password.length > 7) {
      var isSimilarEmail = true;
      var isSimilarUserName = true;
      var firstnameCopy = "";
      var lasNameCopy = "";
      if (firstname) firstnameCopy = firstname;
      if (lastname) lasNameCopy = lastname;
      if (
        JaroWrinker(
          password.toUpperCase(),
          firstnameCopy.toUpperCase() + lasNameCopy.toUpperCase()
        ) >= 0.9071428571428571 ||  JaroWrinker(
          password.toUpperCase(),
          lasNameCopy.toUpperCase() +  firstnameCopy.toUpperCase()
        ) >= 0.9071428571428571
      ) {
        checkpassword.classList.remove("fa-check");
        $(`#password_container `).addClass("error-input-field");
        $(`#password_helper span `).text(
          "Le mot de passe est trop semblable a votre nom et prénom"
        );
        isSimilarUserName = true;
      } else isSimilarUserName = false;
      if (
        JaroWrinker(password.toUpperCase(), email.toUpperCase()) >=
        0.9071428571428571 || 
        JaroWrinker(password.toUpperCase(), email.split("@")[0].toUpperCase()) >=
        0.9071428571428571 ||
        JaroWrinker(password.toUpperCase(), email.split("@")[1].split(".")[0].toUpperCase()) >=
        0.9071428571428571 
  
      ) {
        checkpassword.classList.remove("fa-check");
        $(`#password_container `).addClass("error-input-field");
        $(`#password_helper span `).text(
          "Le mot de passe est trop semblable a votre email"
        );
        isSimilarEmail = true;
      } else {
        isSimilarEmail = false;
      }
  
      //remove error if not similar
      if (isSimilarEmail == false && isSimilarUserName == false) {
        strength += 1;
        checkpassword.classList.add("fa-check");
        $(`#password_container `).removeClass("error-input-field");
        $(`#password_helper `).append("");
      }
    }
  
    //////////////////////////////////////////////
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
      passwordStrength.style = "width: 20%";
      nivLevel.innerHTML = "faible";
      nivLevel.classList.add("niv-level-1");
      nivLevel.classList.remove("niv-level-3");
      nivLevel.classList.remove("niv-level-2");
    } else if (strength == 2) {
      passwordStrength.classList.remove("progress-bar-success");
      passwordStrength.classList.remove("progress-bar-danger");
      passwordStrength.classList.add("progress-bar-warning");
      passwordStrength.style = "width: 40%";
      nivLevel.innerHTML = "moyenne";
      nivLevel.classList.add("niv-level-2");
      nivLevel.classList.remove("niv-level-1");
      nivLevel.classList.remove("niv-level-3");
    } else if (strength == 3) {
      passwordStrength.classList.remove("progress-bar-success");
      passwordStrength.classList.remove("progress-bar-danger");
      passwordStrength.classList.add("progress-bar-warning");
      passwordStrength.style = "width: 60%";
      nivLevel.innerHTML = "moyenne";
      nivLevel.classList.add("niv-level-2");
      nivLevel.classList.remove("niv-level-1");
      nivLevel.classList.remove("niv-level-3");
    } else if (strength == 4) {
      passwordStrength.classList.remove("progress-bar-success");
      passwordStrength.classList.remove("progress-bar-danger");
      passwordStrength.classList.add("progress-bar-warning");
      passwordStrength.style = "width: 80%";
      nivLevel.innerHTML = "moyenne";
      nivLevel.classList.add("niv-level-2");
      nivLevel.classList.remove("niv-level-1");
      nivLevel.classList.remove("niv-level-3");
    } else if (strength == 5) {
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
  
  // Jaro-Winkler Algorithm for similarity comparison
(function () {
    JaroWrinker = function (s1, s2) {
      var m = 0;
  
      // Exit early if either are empty.
      if (s1.length === 0 || s2.length === 0) {
        return 0;
      }
  
      // Exit early if they're an exact match.
      if (s1 === s2) {
        return 1;
      }
  
      var range = Math.floor(Math.max(s1.length, s2.length) / 2) - 1,
        s1Matches = new Array(s1.length),
        s2Matches = new Array(s2.length);
  
      for (i = 0; i < s1.length; i++) {
        var low = i >= range ? i - range : 0,
          high = i + range <= s2.length ? i + range : s2.length - 1;
  
        for (j = low; j <= high; j++) {
          if (s1Matches[i] !== true && s2Matches[j] !== true && s1[i] === s2[j]) {
            ++m;
            s1Matches[i] = s2Matches[j] = true;
            break;
          }
        }
      }
  
      // Exit early if no matches were found.
      if (m === 0) {
        return 0;
      }
  
      // Count the transpositions.
      var k = (n_trans = 0);
  
      for (i = 0; i < s1.length; i++) {
        if (s1Matches[i] === true) {
          for (j = k; j < s2.length; j++) {
            if (s2Matches[j] === true) {
              k = j + 1;
              break;
            }
          }
  
          if (s1[i] !== s2[j]) {
            ++n_trans;
          }
        }
      }
  
      var weight = (m / s1.length + m / s2.length + (m - n_trans / 2) / m) / 3,
        l = 0,
        p = 0.1;
  
      if (weight > 0.7) {
        while (s1[l] === s2[l] && l < 4) {
          ++l;
        }
  
        weight = weight + l * p * (1 - weight);
      }
  
      return weight;
    };
  })();