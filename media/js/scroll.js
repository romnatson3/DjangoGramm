let url_scroll = `${document.location['origin']}/scroll/`
let headers = {'Content-Type': 'application/json',
               'X-Requested-With': 'XMLHttpRequest',
               'X-CSRFToken': get_csrftoken()}

function get_csrftoken (){
    let cookies = document.cookie.split(';')
    let d = {}
    for (let i in cookies) {
        let item = cookies[i].split('=')
        d[item[0].trim()] = item[1]
    }
    return d['csrftoken']
}

async function sendRequest(post_id) {
    try {
    let response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({'post_id': post_id}),
    })
    let result = await response.json()
        if (response.ok) {
            return result
        }
    } catch (error) {
        console.log(error)        
    }
}


//let pp = Math.ceil(window.pageYOffset/window.innerHeight) 
//let pp = window.innerHeight
//console.log(pp)


//window.onclick = function(e) {
//    let result = e.target.id.match('post_id_([0-9]*)$')
//    if (result) {
//        sendRequest(result[1]).then(data => {
//            e.target.innerText = data['like_count']
//            if (data['like']) {
//                e.target.className = "bi bi-hand-thumbs-up-fill h5"
//            } else {
//                e.target.className = "bi bi-hand-thumbs-up h5"
//            }
//        })
//    }
//}
