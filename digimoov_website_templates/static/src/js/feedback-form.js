$(document).ready(function () {
  //popup's message depends with partner has documents
  document.getElementById("hasdocument").value == "True"
    ? (document.getElementById("notifMessage").textContent =
        "Vous pourrez désormais choisir votre date et centre d'examen et financer votre formation.")
    : (document.getElementById("notifMessage").textContent =
        "Pour passer à l'étape suivante merci de vous munir d'une copie originale de votre carte d'identité.");
  console.log(hasdocument, document.getElementById("hasdocument").value);
  console.log(
    window.location.href.includes("/coordonnees#popup1"),
    window.location.href
  );
  if (window.location.href.includes("/coordonnees#popup1")) {
    console.log("enter");
    window.location.href = "/coordonnees";
  }
  var current_fs, next_fs, previous_fs; //fieldsets
  var opacity;
  var current = 1;
  fixStepIndicator(0);

  //   var steps = $("fieldset").length;
  var pass;

  const group1 = $("input[type=radio][name=group1]");
  const group2 = $("input[type=radio][name=group2]");
  const group3 = $("input[type=radio][name=group3]");
  //   const textarea1 = $("#text1");
  const textarea2 = $("#text2");
  var error;

  $(".next").click(function (event) {
    event.preventDefault();

    switch (current) {
      case 1:
        pass = check("group1");
        error = $("#error1");
        break;
      case 2:
        pass = check("group2");
        error = $("#error2");
        break;
      case 3:
        pass = check("group3");
        error = $("#error3");
        break;
      case 4:
        pass = textarea2.val();
        error = $("#error4");
        break;
    }

    console.log(pass);
    if (pass) {
      current_fs = $(this).parent().parent();
      next_fs = $(this).parent().parent().next();
      // 4 is the final step
      // if partner has documents submit the form if not show the notification popup
      if (current == 4) {
        pass = 0;
        error.text("");
        error.hide();
        //show popup
        window.location.href = "#popup1";
        return false;
      }
      if (current == 4) return;
      next_fs.show();
      //hide the current fieldset with style
      current_fs.animate(
        { opacity: 0 },
        {
          step: function (now) {
            // for making fielset appear animated
            opacity = 1 - now;

            current_fs.css({
              display: "none",
              position: "relative",
            });
            next_fs.css({ opacity: opacity });
          },
          duration: 500,
        }
      );
      //   document.getElementsByClassName("step")[current - 1].className +=
      //     " finish";
      ++current;
      fixStepIndicator(current - 1);

      pass = 0;
      error.text("");
      error.hide();
    }

    // if (pass.length > 1 && current === 4) {
    //   console.log(pass.length);
    else {
      error.text("Veuillez répondre à la question");
      error.show();
    }
  });

  //determine which filedset is the previous
  $(".previous").click(function () {
    current_fs = $(this).parent().parent();
    previous_fs = $(this).parent().parent().prev();

    //Remove class active

    //show the previous fieldset
    previous_fs.show();

    //hide the current fieldset with style
    current_fs.animate(
      { opacity: 0 },
      {
        step: function (now) {
          // for making fielset appear animation
          opacity = 1 - now;

          current_fs.css({
            display: "none",
            position: "relative",
          });
          previous_fs.css({ opacity: opacity });
        },
        duration: 500,
      }
    );
    --current;
    fixStepIndicator(current - 1);
  });

  //Determine if user has checked a box or not
  function check(name) {
    let category = document.getElementsByName(name);
    let check = 0;
    for (i = 0; i < category.length; i++) {
      if (category[i].checked) {
        check = 1;
        break;
      }
    }
    return check;
  }

  function fixStepIndicator(n) {
    // Removes the "active" class of all steps...
    var i,
      x = document.getElementsByClassName("step");
    for (i = 0; i < x.length; i++) {
      x[i].className = x[i].className.replace(" active", "");
    }
    //... and adds the "active" class on the current step:
    x[n].className += " active";
  }
});
