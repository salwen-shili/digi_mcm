$(document).ready(function () {
  showTab(0); // Display the current tab

  //

  //
  //setProgress BAR
  $(".progress-bar").css("width", "25%");
  //
  var validSubmit = {
    firstname_valid: false,
    lastname_valid: false,
    phone_valid: false,
    email: false,
    confirmemail_valid: false,
    password_valid: false,
  };
  const buttonInscrire = document.getElementById("inscrire");

  //check only letteres
  function checkLetters(prop, value) {
    if (value.length > 0) {
      const pattern = /^[A-Z,a-z,À-ÿ '-]{2,}$/;
      if (value.match(pattern)) return false;
      else return `Votre ${prop} doit contenir des lettres seulement!`;
    } else return "Ce champs est obligatoire!";
  }

  //check phone number
  function checkPhone(prop, value) {
    if (value.length > 0) {
      const pattern = /^(07|06)[0-9]\d{7}$/;
      if (value.match(pattern)) return false;
      else
        return `Votre numéro de téléphone doit commencer par 06 ou 07 suivie par 8 chiffres`;
    } else return "Ce champs est obligatoire!";
  }

  function checkEmail(email, confirm_email) {
    const pattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if (email.length > 0) {
      if (email.match(pattern)) {
        $(`#email_container `).removeClass("error-input-field");
        $(`#email_helper `).append("");
      } else {
        $(`#email_container `).addClass("error-input-field");
        $(`#email_helper span `).text("Votre email est incorrecte!");
      }
    } else {
      $(`#email_container `).addClass("error-input-field");
      $(`#email_helper span `).text("Ce champs est obligatoire!");
    }

    if (confirm_email.length > 0) {
      if (confirm_email.match(pattern)) {
        $(`#confirm_email_container `).removeClass("error-input-field");
        $(`#confirm_email_helper `).append("");
      } else {
        $(`#confirm_email_container `).addClass("error-input-field");
        $(`#confirm_email_helper span `).text("Votre email est incorrecte!");
      }
    } else {
      $(`#confirm_email_container `).addClass("error-input-field");
      $(`#confirm_email_helper span `).text("Ce champs est obligatoire!");
    }
    if (email.length > 0 && confirm_email.length > 0) {
      if (email === confirm_email) {
        if (confirm_email.match(pattern)) {
          $(`#email_container `).removeClass("error-input-field");
          $(`#email_helper `).append("");
          $(`#confirm_email_container `).removeClass("error-input-field");
          $(`#confirm_email_helper `).append("");
        }
      } else {
        //console.log('email !== confirm_email');
        //console.log(email, '  ', confirm_email);
        $(`#confirm_email_container `).addClass("error-input-field");
        $(`#confirm_email_helper span `).text(
          "L'email ne correspond pas au champs precedent! Veuillez confirmer votre email."
        );
      }
    }
  }

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

  //**************************************************************************************** */
  //event Handler
  //**************************************************************************************** */

  $(`#lastname`).keyup(function (e) {
    const lastname = $("#lastname").val();
    const errorMessage = checkLetters("nom", lastname);
    if (errorMessage === false) {
      validSubmit["lastname_valid"] = true;

      if (checkValidationButton(validSubmit)) {
        // buttonInscrire.removeAttribute("disabled");
      }
      $(`#lastname_container `).removeClass("error-input-field");
      $(`#lastname_helper `).append("");
    } else {
      validSubmit["lastname_valid"] = false;
      // buttonInscrire.setAttribute("disabled", "disabled");

      $(`#lastname_container `).addClass("error-input-field");
      $(`#lastname_helper span `).text(errorMessage);
    }
  });

  $(`#firstname`).keyup(function (e) {
    const firstname = $("#firstname").val();
    const errorMessage = checkLetters("prenom", firstname);
    if (errorMessage === false) {
      validSubmit["firstname_valid"] = true;

      if (checkValidationButton(validSubmit)) {
        // buttonInscrire.removeAttribute("disabled");
      }
      $(`#firstname_container `).removeClass("error-input-field");
      $(`#firstname_helper `).append("");
    } else {
      validSubmit["firstname_valid"] = false;
      // buttonInscrire.setAttribute("disabled", "disabled");

      $(`#firstname_container `).addClass("error-input-field");
      $(`#firstname_helper span `).text(errorMessage);
    }
  });

  $(`#phone`).keyup(function (e) {
    const phone = $("#phone").val();
    const errorMessage = checkPhone("numero de téléphone", phone);
    if (errorMessage === false) {
      validSubmit["phone_valid"] = true;

      if (checkValidationButton(validSubmit)) {
        // buttonInscrire.removeAttribute("disabled");
      }

      $(`#phone_container `).removeClass("error-input-field");
      $(`#phone_helper `).append("");
    } else {
      validSubmit["phone_valid"] = false;
      // buttonInscrire.setAttribute("disabled", "disabled");

      $(`#phone_container `).addClass("error-input-field");
      $(`#phone_helper span `).text(errorMessage);
    }
  });

  $(`#email`).keyup(function (e) {
    const email = $("#email").val();
    const confirm_email = $("#confirm_email").val();
    checkEmail(email, confirm_email);
  });

  $(`#confirm_email`).keyup(function (e) {
    const email = $("#email").val();
    const confirm_email = $("#confirm_email").val();
    checkEmail(email, confirm_email);
  });

  $(`#password`).keyup(function (e) {
    showPasswordPopover();
    const password = $("#password").val();
    const errorMessage = checkPassword(password);
    if (errorMessage === false) {
      validSubmit["password_valid"] = true;

      if (checkValidationButton(validSubmit)) {
        // buttonInscrire.removeAttribute("disabled");
      }

      $(`#password_container `).removeClass("error-input-field");
      $(`#password_helper `).append("");
    } else {
      validSubmit["password_valid"] = false;
      // buttonInscrire.setAttribute("disabled", "disabled");

      $(`#password_container `).addClass("error-input-field");
      $(`#password_helper span `).text(errorMessage);
    }
    checkStrength(password);
  });

  function checkValidationButton(valid) {
    const toArray = Object.keys(valid).map((key, index) => {
      return valid[key];
    });
    // console.log(valid);
    // console.log("validation", toArray);
    for (let index = 0; index < toArray.length; index++) {
      if (toArray[index] === false) return false;
    }

    return true;
  }

  //Validate Address

  const apiCommunes = "https://geo.api.gouv.fr/communes?codePostal=";
  const apiVoie = "https://api-adresse.data.gouv.fr/search/?q=";
  const format = "&format=json";
  let checked = false;
  let zipcode = $("#zipcode");
  let city = $("#city");
  let voie = $("#voie");
  let typeVoie = $("#voie");
  let nomVoie = $("#nom_voie");
  let introuvable = $("#introuvable");
  $(introuvable).click(function () {
    checked = !checked;
    if (checked) {
      $("#nom_voie_container")
        .html(`<input type="text" name="nom_voie" id="nom_voie" class="outlined-text-field"  value="" required="required" inputmode="latin" autocomplete="off"  />
                        <label for="nom_voie">Nom de voie *</label>
                        <i class="material-icons error-icon">error_outline</i>
                        <div class="helper-text bg-c " id="nom_voie_helper">
                          <span></span>
                        </div>`);
      $("#voie_container")
        .html(` <input type="text" id="voie" class="outlined-text-field" value="" required="required" autocomplete="off" inputmode="latin"  />
                        <label for="voie">Type de voie *</label>
                        <i class="material-icons error-icon">error_outline</i>
                        <div class="helper-text bg-c " id="voie_helper">
                          <span></span>
                        </div> `);
    }

    const listId = [
      "lastname",
      "firstname",
      "phone",
      "address",
      "email",
      "confirm_email",
      "password",
      "zipcode",
      "city",
      "voie",
      "voie_input",
      "nom_voie",
      "num_voie",
      "comp_address",
    ];
    listId.map((id) => {
      $(`#${id}`).focusin(function () {
        $(`#${id} ~ label`).animate(
          {
            fontSize: "0.8rem",
            top: "-0.7rem",
            padding: "0.25rem",
          },
          80
        );
      });
      $(`#${id}`).focusout(function () {
        if ($(this).val() === "") {
          $(`#${id} ~ label`).animate(
            {
              fontSize: "1rem",
              top: "1rem",
              padding: 0,
            },
            80
          );
        }
      });
    });
  });

  $(zipcode).on("blur", function () {
    var code = $(this).val();
    //console.log(code);
    let url = apiCommunes + code + format;
    //console.log(url);

    fetch(url, { method: "get" })
      .then((response) => response.json())
      .then((results) => {
        //console.log(results);
        $(city).find("option").remove();
        if (results.length) {
          $(`#city_container `).removeClass("error-input-field");
          $(`#city `).removeClass("error-input-field");
          $(`#city_helper `).append("");
          $("#city_container").removeAttr("aria-disabled");
          $(city).removeAttr("disabled");
          $(voie).removeAttr("disabled");
          $(city).focus();
          $.each(results, function (key, value) {
            //console.log(value);
            // console.log(value.nom);
            $(city).removeAttr("disbaled");

            $(city).append(
              '<option value="' + value.nom + '">' + value.nom + "</option>"
            );
          });
        } else {
          if ($(zipcode).val()) {
            $("#city_container").attr(`aria-disabled="true"`);
            $(city).attr(`disbaled="disabled"`);
            $(voie_container).attr(`disbaled="disabled"`);
            $(voie).attr(`disbaled="disabled"`);
            $(`#city_container `).addClass("error-input-field");
            $(`#city `).addClass("error-input-field");
            $(`#city_helper span`).text("Aucune commmune avec ce code postal.");
          } else {
            $(`#city_container `).removeClass("error-input-field");
            $(`#city `).removeClass("error-input-field");
            $(`#city_helper `).append("");
            $("#city_container").removeAttr(`aria-disabled="true"`);
            $(city).removeAttr(`disbaled="disabled"`);
            $(voie_container).removeAttr(`disbaled="disabled"`);
            $(voie).removeAttr(`disbaled="disabled"`);
          }
        }
      })
      .catch((err) => {
        // console.log(err);
        $(city).find("option").remove();
      });
  });

  // $("#first_form").submit(function (e) {
  //   //document.querySelector('.error-input-field').scrollIntoView();
  //   //document.getElementById('.password').scrollIntoView();
  //   const hasError =
  //     document.querySelector(".error-input-field") != null ? true : false;
  //   const passwordHasError =
  //     document.querySelector(".niv-level-3") == null ? true : false;
  //   if (hasError || passwordHasError) {
  //     e.preventDefault();
  //     if (document.querySelector(".error-input-field")) {
  //       document.querySelector(".error-input-field").scrollIntoView();
  //     } else if (passwordHasError) {
  //       document.getElementById("password").scrollIntoView();
  //     }
  //     return;
  //   } else {
  //   }
  // });

  //for resettting password
  $("form").submit(function (e) {
    //document.querySelector('.error-input-field').scrollIntoView();
    //document.getElementById('.password').scrollIntoView();
    const hasError =
      document.querySelector(".error-input-field") != null ? true : false;
    const passwordHasError =
      document.querySelector(".niv-level-3") == null ? true : false;
    if (hasError || passwordHasError) {
      e.preventDefault();
      if (document.querySelector(".error-input-field")) {
        document.querySelector(".error-input-field").scrollIntoView();
      } else if (passwordHasError) {
        document.getElementById("password").scrollIntoView();
      }
      return;
    } else {
    }
  });
});
let state = false;
let password = document.getElementById("password");
let passwordStrength = document.getElementById("password-strength");
let lowUpperCase = document.querySelector(".low-upper-case i");
let number = document.querySelector(".one-number i");
let specialChar = document.querySelector(".one-special-char i");
let checkpassword = document.querySelector(".checkpassword i");
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

function showTab(n) {
  console.log("show tab", n);
  // This function will display the specified tab of the form...
  var x = document.getElementsByClassName("tab");
  x[n].style.display = "block";
  //... and fix the Previous/Next buttons:
  if (n == 0) {
    document.getElementById("prevBtn").style.display = "none";
  } else {
    document.getElementById("prevBtn").style.display = "inline";
  }
  if (n == x.length - 1) {
    document.getElementById(
      "nextBtn"
    ).innerHTML = `S'inscrire<i class="material-icons right"> keyboard_arrow_right</i>`;
    document.getElementById(
      "nextBtn"
    ).type="submit"
  } else {
    document.getElementById(
      "nextBtn"
    ).innerHTML = `Suivant<i class="material-icons right"> keyboard_arrow_right</i>`;
  }
  //... and run a function that will display the correct step indicator:
  fixStepIndicator(n);
}
var currentTab = 0; // Current tab is set to be the first tab (0)

// function next(e){
// nextPrev(1);
// e.preventDefault();

// }

function nextPrev(n) {
  // if you have reached the end of the form...
  if (currentTab == 1 && n == 1) {
    // ... the form gets submitted:
     
    
    return false;
  }
  // e.preventDefault();
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("tab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;
  // Hide the current tab:
  x[currentTab].style.display = "none";
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;

  // Otherwise, display the correct tab:
  showTab(currentTab);
}

function validateForm() {
  // This function deals with validation of the form fields

  var valid = false;
  if (
    document.querySelector(".error-input-field") == null &&
    document.querySelector(".niv-level-3") != null
  )
    valid = true;

  var elements = document.getElementById("fields1");

  for (var i = 0, element; (element = elements[i++]); ) {
    if (element.checkValidity() == false) {
      element.scrollIntoView({ block: "start" });
      console.log(element, element.checkValidity());
      valid = false;
    }
  }
  // If the valid status is true, mark the step as finished and valid:
  if (valid) {
    document.getElementsByClassName("step")[currentTab].className += " finish";
  }
  if (document.querySelector(".error-input-field") != null)
    document
      .querySelector(".error-input-field")
      .scrollIntoView({ behavior: "smooth", block: "center" });
  else if (document.querySelector(".niv-level-3") == null)
    document
      .getElementById("password")
      .scrollIntoView({ behavior: "smooth", block: "center" });

  return valid; // return the valid status
}



function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i,
    x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class on the current step:
  x[n].className += " active";
}
