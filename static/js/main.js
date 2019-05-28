function render_book_list(response)
{
    let search_results_div =  document.querySelector(".book-list")

    search_results_div.innerHTML = "";

    let book_list = document.createElement("ul");

    for(let book in response.list)
    {
        // Iterate though every element of the list and convert it to html
        
        let li = document.createElement("li");

        li.innerHTML = `<h2> <a href="/books/${response.list[book].isbn_number}"> ${response.list[book].title} </a>  </h2>`

        book_list.appendChild(li);
    }

    document.querySelector(".book-list").appendChild(book_list);
}


function render_new_review(response)
{
    let reviews =  document.querySelector(".reviews")

    if(document.querySelectorAll(".review").length === 0)
    {
        reviews.innerHTML = ""
    }

    let review = document.createElement("div");

    review.classList.add("review", "alert", "alert-primary")

    review.innerHTML = `
            <header>
                ${ response.username }
                <span>Score: ${ response.rating }</span>
            </header>
        <p>${ response.review_description }</p>
    `

    reviews.appendChild(review);

    // After appending the new review
    //slideUp(element,{
    //    duration: 2500
    //});

    // Remove Element
    review.parentNode.removeChild(review);
}

function render_message(error, container)
{
    let div =  document.querySelector(container)

    div.innerHTML = error.responseJSON.message
}

function ajax_search(event)
{
    event.preventDefault();

    // Compatiblity Problems
    form_url = window.location.href

    $.ajax({
        url: form_url,
        data: $('#' + event.target.id).serialize(),
        type: 'POST',
        success: function(response) {
            render_book_list(response)
        },
        error: function(response) {
            render_message(response, ".book-list");
        }
    });
}

// function fetch_review_form(event)
// {
//     event.preventDefault();

//     const data = new URLSearchParams();
//     for (const pair of new FormData(event.target)) {
//         data.append(pair[0], pair[1]);
//     }

//     let headers = new Headers();

//     let miInit = { method: 'POST',
//                   headers: headers,
//                   body: data,
//                   mode: 'cors',
//                   cache: 'default' };

//     fetch(event.originalTarget.action, miInit)
//     .then(result => 
//     {
//         if(result.ok)
//         {
//             console.log('success:', result)
    
//             return result
//         }
//     })
//     .then(result =>
//     {
//         console.log(result)
//     })
//     .catch(error =>
//     {
//         console.log("Error", error)
//     });
// }

function fetch_review_form(event)
{
    event.preventDefault();

    // Compatiblity Problems
    form_url = window.location.href

    $.ajax({
        url: form_url,
        data: $('#' + event.target.id).serialize(),
        type: 'POST',
        success: function(response) {
            console.log(response)
            render_new_review(response)
        },
        error: function(response) {
            render_message(response, ".message");
        }
    });
}


document.addEventListener("DOMContentLoaded", function()
{
    if(window.location.pathname === "/search")
    {
        document.querySelector("#search_form").addEventListener("submit", ajax_search)
    }

    if(window.location.pathname.indexOf("/books/") == 0 && document.querySelector("#review-form"))
    {
        document.querySelector("#review-form").addEventListener("submit", fetch_review_form)
    }
});
