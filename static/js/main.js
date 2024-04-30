function show_me(id, type )
{
  var id = id;
  var type = type;
  var data = confirm("Вы хотите удалить это?");
  if (data){
    window.location.href = "../../remove_item/" + type + "/"+ id;}

};
async function addToBasket(product_id, user_id = 0) {
//       var data = confirm("Вы хотите удалить это?");
  const response = await fetch('./api/add_product', {
    method: 'POST',
    body: JSON.stringify({'product_id': product_id, 'user_id': user_id}),
    headers: {
      'Content-Type': 'application/json'
    }
  });

  const myJson = await response.json();
};

async function removeFromBasket(product_id, user_id = 0) {
  const response = await fetch('../api/remove_product', {
    method: 'POST',
    body: JSON.stringify({'product_id': product_id, 'user_id': user_id}),
    headers: {
      'Content-Type': 'application/json'
    }
  });

  const myJson = await response.json();
};
async function minusFromBasket(product_id, user_id = 0) {
  const response = await fetch('../api/minus_product', {
    method: 'POST',
    body: JSON.stringify({'product_id': product_id, 'user_id': user_id}),
    headers: {
      'Content-Type': 'application/json'
    }
  });

  const myJson = await response.json();
};
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
*/