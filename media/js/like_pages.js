var headers = {'Content-Type': 'application/json',
               'X-Requested-With': 'XMLHttpRequest',
               'X-CSRFToken': get_csrftoken()}
var post_id
var todo
var page = 1


function get_body() { 
    if (todo == 'like') {
        var body = {'post_id': post_id}
    } else if (todo == 'scroll') {
        var body = {'page': page}
    }
    return JSON.stringify(body)
}


function get_csrftoken (){
    var cookies = document.cookie.split(';')
    var d = {}
    for (var i in cookies) {
        var item = cookies[i].split('=')
        d[item[0].trim()] = item[1]
    }
    return d['csrftoken']
}


async function sendRequest() {
    try {
    var url = `${document.location['origin']}/${todo}/`
    var response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: get_body(todo),
    })
    var result = await response.json()
        if (response.ok) {
            return result
        }
    } catch (error) {
        console.log(error)        
    }
}


window.onclick = function(e) {
    todo = 'like'
    var result = e.target.id.match('post_id_([0-9]*)$')
    if (result) {
        post_id = result[1]
        sendRequest().then(data => {
            if (data) {
                e.target.innerText = data['like_count']
                if (data['like']) {
                    e.target.className = "bi bi-hand-thumbs-up-fill h5"
                } else {
                    e.target.className = "bi bi-hand-thumbs-up h5"
                }
            }
        })
    }
}


window.addEventListener('scroll', function(e) {
    todo = 'scroll'
    if (document.body.scrollHeight - window.pageYOffset == window.innerHeight) {
        page += 1
        console.log(page)
        sendRequest().then(data => {
            if (data) {
                var container = document.getElementById('container')
                for (var i in data) {
                    console.log(data[i])
                    var card = document.createElement('div')
                    card.className = 'card mb-3 mx-3'
                    card.style.width = '40%'
                    card.style.float = 'left'
                    var btn = document.createElement('div')
                    btn.className = 'btn btn-primary position-relative position-absolute top-0 start-0'
                    var like = document.createElement('span')
                    if (data[i]['like']) {
                        like.className = 'bi bi-hand-thumbs-up-fill h5'
                    } else {
                        like.className = 'bi bi-hand-thumbs-up h5'
                    }
                    like.innerText = data[i]['like_count']
                    like.id = `post_id_${data[i]['post_id']}`
                    btn.appendChild(like)
                    var img = document.createElement('img')
                    img.className = 'card-img-top'
                    img.src = data[i]['photo']
                    card.appendChild(btn)
                    card.appendChild(img)
                    var card_body = document.createElement('div')
                    card_body.className = 'card-body'
                    var card_text_1 = document.createElement('p')
                    card_text_1.className = 'card-text'
                    card_text_1.innerText = data[i]['datetime']
                    card_body.appendChild(card_text_1)
                    var card_text_2 = document.createElement('p')
                    card_text_2.className = 'card-text'
                    card_text_2.innerText = data[i]['description']
                    card_body.appendChild(card_text_2)
                    card.appendChild(card_body)
                    container.appendChild(card)
                    var str = `<b><a href="profile/${data[i]['username']}"><img src="${data[i]['avatar']}" width="40px" height="40px">${data[i]['username']}</a></b>`
                    if (document.location.href.search('profile') || document.location.href.search('my_post')) {
                        null
                    } else {
                        card_body.insertAdjacentHTML('beforeend', str)
                    }
                }
            }
        })
    }
})

