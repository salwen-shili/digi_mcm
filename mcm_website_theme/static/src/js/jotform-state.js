window.addEventListener('message', receiveMessage, false);
function receiveMessage(event) {
  console.log('event.data.status: _ ', event.data.status);
}
