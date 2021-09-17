// move label on focus
document.addEventListener("DOMContentLoaded", function () {
  const listId = [
    "lastname",
    "firstname",
    "phone",

    "email",
    "confirm_email",
    "password",
    "zipcode",
    "city",
    "voie",
    // "voie_input",
    "nom_voie",
    "num_voie",
    "comp_address",
    // "login",
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

  // listId.map((id) => {
  //   $("#form_input").on("input", "`"#${id}"`", function () {
  //     console.log("dkhal");
  //     if ($(this).val().length) {
  //       var hasVal = true;
  //     } else {
  //       var hasVal = false;
  //     }
  //     console.log(
  //       "Input has value (true / false): ",
  //       hasVal + " (" + $(this).val() + ")"
  //     );
  //   });
  // });

  listId.map((id) => {
    if ($(`#${id}`).val()) {
      $(`#${id} ~ label`).animate(
        {
          fontSize: "0.8rem",
          top: "-0.7rem",
          padding: "0.25rem",
        },
        80
      );
    }
  });

  // listId.map((id) => {
  //   console.log(id);
  //   if (id === "city" || id === "voie_container") return;
  //   if (id === "confirm_email" || id === "password") return;
  //   else {
  //     const input = $(`#${id}`);
  //     const inputVal = input.val();
  //     console.log(id);
  //     if (inputVal.length) {
  //       console.log(inputVal.length, inputVal);
  //       // $(`#${id} ~ label`).animate(
  //       //   {
  //       //     fontSize: "1rem",
  //       //     top: "1rem",
  //       //     padding: 0,
  //       //   },
  //       //   80
  //       // );
  //     }
  //   }
  // });

  /* -----------------------------------------------------
  Material Design Buttons
-------------------------------------------------------- */
  $(document).ready(function () {
    $(".ripple-effect").rkmd_rippleEffect();
  });

  (function ($) {
    $.fn.rkmd_rippleEffect = function () {
      var btn, self, ripple, size, rippleX, rippleY, eWidth, eHeight;

      btn = $(this).not("[disabled], .disabled");

      btn.on("mousedown", function (e) {
        self = $(this);

        // Disable right click
        if (e.button === 2) {
          return false;
        }

        if (self.find(".ripple").length === 0) {
          self.prepend('<span class="ripple"></span>');
        }
        ripple = self.find(".ripple");
        ripple.removeClass("animated");

        eWidth = self.outerWidth();
        eHeight = self.outerHeight();
        size = Math.max(eWidth, eHeight);
        ripple.css({ width: size, height: size });

        rippleX = parseInt(e.pageX - self.offset().left) - size / 2;
        rippleY = parseInt(e.pageY - self.offset().top) - size / 2;

        ripple
          .css({ top: rippleY + "px", left: rippleX + "px" })
          .addClass("animated");

        setTimeout(function () {
          ripple.remove();
        }, 800);
      });
    };
  })(jQuery);
});
