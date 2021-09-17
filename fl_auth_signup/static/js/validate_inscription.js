$(document).ready(function () {
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
    // codepostal_valid: false,
    // ville_valid: false,
    // voieType_valid: false,
    // voieNom_valid: false,
  };
  const buttonInscrire = document.getElementById("inscrire");

  //check only letteres
  function checkLetters(prop, value) {
    if (value.length > 0) {
      const pattern = /^[A-Z,a-z,À-ÿ '-]{2,}$/;
      if (value.match(pattern)) return false;
      else return `Votre ${prop} doit contenir des lettres seulement!`;
    } else return "Ce champ est obligatoire!";
  }

  //check phone number
  function checkPhone(prop, value) {
    if (value.length > 0) {
      const pattern = /^(07|06)[0-9]\d{7}$/;
      if (value.match(pattern)) return false;
      else
        return `Votre numéero de téléphone doit commencer par 06 ou 07 suivie par 8 chiffres`;
    } else return "Ce champ est obligatoire!";
  }

  function checkEmail(prop, value) {
    if (value.length > 0) {
      const pattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
      if (value.match(pattern)) return false;
      else return `Votre ${prop} est incorrecte!`;
    } else return "Ce champ est obligatoire!";
  }

  function checkConfirmEmail(value, confirmValue) {
    if (value.length > 0) {
      if (value === confirmValue) return false;
      else return `L'email ne correspond pas! Vuillez confirmer votre email.`;
    } else return "Ce champ est obligatoire!";
  }

  function checkPassword(value) {
    if (value.length > 0) {
      if (value.length < 8)
        return "Votre mot de passe doit contenir au minimum 8 caractères";
      else {
        const pattern =
          /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!/+/='":;(){}[|@$ %^&*-]).{8,}$/;
        if (value.match(pattern)) return false;
        else
          return `Votre mot de passe doit contenir une combinaison de chiffres, caractères spéciaux, lettres majuscules et minuscules!`;
      }
    } else return "Ce champ est obligatoire!";
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
        buttonInscrire.removeAttribute("disabled");
      }
      $(`#lastname_container `).removeClass("error-input-field");
      $(`#lastname_helper `).append("");
    } else {
      validSubmit["lastname_valid"] = false;
      buttonInscrire.setAttribute("disabled", "disabled");

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
        buttonInscrire.removeAttribute("disabled");
      }
      $(`#firstname_container `).removeClass("error-input-field");
      $(`#firstname_helper `).append("");
    } else {
      validSubmit["firstname_valid"] = false;
      buttonInscrire.setAttribute("disabled", "disabled");

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
        buttonInscrire.removeAttribute("disabled");
      }

      $(`#phone_container `).removeClass("error-input-field");
      $(`#phone_helper `).append("");
    } else {
      validSubmit["phone_valid"] = false;
      buttonInscrire.setAttribute("disabled", "disabled");

      $(`#phone_container `).addClass("error-input-field");
      $(`#phone_helper span `).text(errorMessage);
    }
  });

  $(`#email`).keyup(function (e) {
    const email = $("#email").val();
    const errorMessage = checkEmail("email", email);
    if (errorMessage === false) {
      validSubmit["email"] = true;

      if (checkValidationButton(validSubmit)) {
        buttonInscrire.removeAttribute("disabled");
      }

      $(`#email_container `).removeClass("error-input-field");
      $(`#email_helper `).append("");
    } else {
      validSubmit["email"] = false;
      buttonInscrire.setAttribute("disabled", "disabled");

      $(`#email_container `).addClass("error-input-field");
      $(`#email_helper span `).text(errorMessage);
    }
  });

  $(`#confirm_email`).keyup(function (e) {
    const confirm_email = $("#confirm_email").val();
    const errorMessage = checkConfirmEmail($("#email").val(), confirm_email);
    if (errorMessage === false) {
      validSubmit["confirmemail_valid"] = true;

      if (checkValidationButton(validSubmit)) {
        buttonInscrire.removeAttribute("disabled");
      }

      $(`#confirm_email_container `).removeClass("error-input-field");
      $(`#confirm_email_helper `).append("");
    } else {
      validSubmit["confirmemail_valid"] = false;
      buttonInscrire.setAttribute("disabled", "disabled");

      $(`#confirm_email_container `).addClass("error-input-field");
      $(`#confirm_email_helper span `).text(errorMessage);
    }
  });

  $(`#password`).keyup(function (e) {
    const password = $("#password").val();
    const errorMessage = checkPassword(password);
    if (errorMessage === false) {
      validSubmit["password_valid"] = true;

      if (checkValidationButton(validSubmit)) {
        buttonInscrire.removeAttribute("disabled");
      }

      $(`#password_container `).removeClass("error-input-field");
      $(`#password_helper `).append("");
    } else {
      validSubmit["password_valid"] = false;
      buttonInscrire.setAttribute("disabled", "disabled");

      $(`#password_container `).addClass("error-input-field");
      $(`#password_helper span `).text(errorMessage);
    }
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

  // // console.log("valid submit en dehors  ", validSubmit);
  // $("#first_form").submit(function (e) {
  // //   console.log("valid  ", validSubmit);
  //   e.preventDefault();

  // //   console.log(checkValidationButton(validSubmit), "type");
  //   $(this).submit();
  // });

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

  //fetch voie address
  // $(typeVoie).on("blur", function () {
  //   let voieVal = $(this).val();
  // //   console.log(voieVal);
  //   // https://api-adresse.data.gouv.fr/search/?q=cour&type=street&postcode=75001
  //   let url =
  //     apiVoie +
  //     voieVal +
  //     "&type=street&postcode=" +
  //     zipcode.val() +
  //     "&city=" +
  //     city.val();
  // //   console.log(url);

  //   fetch(url, { method: "get" })
  //     .then((response) => response.json())
  //     .then((results) => {
  //       $(nomVoie).find("option").remove();
  //       const filteredResults = results.features.filter(
  //         (val) =>
  //           val.properties.name.split(" ")[0].toUpperCase() ===
  //           voieVal.toUpperCase()
  //       );
  //       //console.log("filter", filteredResults);
  //       const finalResult = filteredResults.map((v) => {
  //         var values = v.properties.name.split(" ");

  //         var subs = values[1]
  //           ? v.properties.name.substr(v.properties.name.indexOf(" ") + 1)
  //           : "";
  //         return subs.charAt(0).toUpperCase() + subs.slice(1) + ` (${voieVal})`;
  //       });
  // //       console.log(finalResult, finalResult.length);
  //       if (finalResult.length) {
  //         $(`#nom_voie_container `).removeClass("error-input-field");
  //         $(`#nom_voie `).removeClass("error-input-field");
  //         $(`#nom_voie_helper `).append("");
  //         $("#nom_voie_container").removeAttr("aria-disabled");
  //         $(nom_voie).removeAttr("disabled");
  //         $(nom_voie).focus();

  // //         //   console.log("finalResult ", finalResult);
  //         $.each(finalResult, function (key, value) {
  //           $(nomVoie).append(
  //             '<option value="' + value + '">' + value + "</option>"
  //           );
  //         });
  //       } else {
  //         $("#nom_voie_container").attr(`aria-disabled="true"`);
  //         $("#nom_voie").attr(`disbaled="disabled"`);
  //         $(`#nom_voie_container `).addClass("error-input-field");
  //         $(`#nom_voie `).addClass("error-input-field");
  //         $(`#nom_voie_helper span`).text("Aucun nom de voie avec ce type.");
  //       }
  //     })
  //     .catch((err) => {
  // //       console.log(err);
  //       $(nomVoie).find("option").remove();
  //     });
  // });
});
