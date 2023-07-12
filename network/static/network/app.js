
const favorites = document.querySelectorAll(".favorite");
const favoriteComment = document.querySelectorAll(".favorite_comment");
const showCommentsBtn = document.querySelectorAll(".show_comments");
const commentsContainer = document.querySelectorAll(".comments_container");


favorites.forEach((favorite) => {
  favorite.onclick = (event) => {
    const userId = favorite.dataset["id"];
    const postId = favorite.dataset["post"];
    const post_path = "/favorite";
    const post_content = { user_id: userId, post_id: postId };
    changeIsFavorite(favorite, post_content, post_path);
  };
});

favoriteComment.forEach((favorite) => {
  favorite.onclick = (event) => {
    const userId = favorite.dataset["id"];
    const postId = favorite.dataset["post"];
    const commentId = favorite.dataset["comment"];
    const post_path = "/favorite_comment";
    const post_content = { user_id: userId, post_id: postId, comment_id: commentId }
    changeIsFavorite(favorite, post_content, post_path)
  };
});

function changeIsFavorite(context, content, path) {
  const choosen_page = context.dataset["page"];
  const author = context.dataset["author"];
  fetch(path, {
    method: "POST",
    body: JSON.stringify(content),
  })
    .then((response) => response.json())
    .then(data => {
      console.log(data)
      if(choosen_page === "index"){
        window.location.href = data.redirect_url;
      } else if (choosen_page === "following") {
        window.location.href = '/following-posts';
      } else if (choosen_page === "user") {
        window.location.href = `/user/${author}`;
      } else {
        console.error("The response not found!")
      }
    })
    .catch((err) => console.log(err));
}

showCommentsBtn.forEach((btn, index) => {
  btn.onclick = (event) => {
    buttonName = btn.innerText
    if(buttonName === 'Show comments') {
      commentsContainer[index].style.display = 'block'
      btn.innerText = 'Hide comments'
    } else if (buttonName === 'Hide comments') {
      commentsContainer[index].style.display = 'none'
      btn.innerText = 'Show comments'
    } else {
      console.error('This button does not exist!!')
    }
  }
})




