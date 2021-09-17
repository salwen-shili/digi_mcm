$(document).ready(function () {
  const cpfDetails = $("#cpf-details");
  const cpfDetails = $("#cpf-details");

  $(cpfDetails).on("click", function () {
    cpfDetails.addClass("hide");
    cpfDetails.removeClass("hide");

    return false;
  });
});

// //YOUTUBE VIDEO
// $('.play-button').click(function(e){
//     var iframeEl = $('<iframe>', { src: $(this).data('url') });
//     $('#youtubevideo').attr('src', $(this).data('url'));
// })

// $('#close-video').click(function(e){
//     $('#youtubevideo').attr('src', '');
// });

// $(document).on('hidden.bs.modal','#myModal', function () {
//     $('#youtubevideo').attr('src', '');
// });
