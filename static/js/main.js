function show_me(id, type , sender = -1)
{
  var id = id;
  var type = type;
  var data = confirm("Вы хотите удалить это?");
  if (data){
    window.location.href = "/remove_item/" + type + "/"+ id + "/"+ sender;}
};
async function addToBasket(product_id, user_id = 0) {
    if (user_id === 0){
    window.location.href="/login"
    }
  else{
  var href = window.location.href;
  const response = await fetch('/api/add_product', {
    method: 'POST',
    body: JSON.stringify({'product_id': product_id, 'user_id': user_id, 'href': href}),
    headers: {
      'Content-Type': 'application/json'
    }
  });
  const myJson = await response.json();
  };
};


async function removeFromBasket(product_id, user_id = 0) {
  const response = await fetch('/api/remove_product', {
    method: 'POST',
    body: JSON.stringify({'product_id': product_id, 'user_id': user_id}),
    headers: {
      'Content-Type': 'application/json'
    }
  });

  const myJson = await response.json();
};

async function minusFromBasket(product_id, user_id = 0) {
  const response = await fetch('/api/minus_product', {
    method: 'POST',
    body: JSON.stringify({'product_id': product_id, 'user_id': user_id}),
    headers: {
      'Content-Type': 'application/json'
    }
  });

  const myJson = await response.json();
};
/*
//async function saveHrefBasket(user_id = 0) {
//    var hrefs = window.location.href;
//    alert('basker')
//      const response = await fetch('/basket', {
//    method: 'POST',
//    body: JSON.stringify({'user_id': user_id, 'href': hrefs}),
//    headers: {
//      'Content-Type': 'application/json'
//    }
//    window.location.href="/basket";
//};

//async function backfromBasket(user_id = 0) {
//    let href;
//    if (sessionStorage.getItem(user_id)) {
//      href = sessionStorage.getItem(user_id);
//    }
//    else{href = '/index'}
//    window.location.href=href
////    console.log(window.history)
////    alert(hrefs[user_id])
////    if (hrefs[user_id]) {window.location.href=hrefs[user_id]}
////    else{window.location.href = '/index'}
//};
*/
async function saveHrefBasket(user_id = 0) {

    try {
        const res = await fetch('/basket', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'href': window.location.href})
        });

        if (res.ok) {
            console.log('Send success!');
        } else {
            throw new Error(`Send error, ${res.statusText}`);
        }
    } catch (error) {
        console.error('Error', error);
    }
    window.location.href = '/basket'
}

/*
const test userAction = async (user_id, product_id) => {
console.log('asdfffd')
  const response = await fetch('http://127.0.0.1:5000/api/add_product/' + user_id + '/' + product_id, {
    method: 'POST',
    body: myBody,
    headers: {
      'Content-Type': 'application/json'
    }
  });
  const myJson = await response.json();
  console.log(myJson)
  //extract JSON from the http response
  // do something with myJson
}

async function saveHrefBasket(user_id = 0) {
    var hrefs = window.location.href;
    window.location.href="/basket";
    let elem = document.getElementById('goFromBasket');
    alert(elem.href)
//    elem.href = hrefs;

};

*/