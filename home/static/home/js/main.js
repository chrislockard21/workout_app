// Sets up the drop downs for exercise lists
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    }
  });
};

// Creates instance of ScrollReveal
var ScrollObject = ScrollReveal({
    reset: false,
});

// Adds the reveal class to the object
ScrollObject.reveal('.reveal', {
    delay: 250,
    origin: 'bottom',
    distance: '20px',
});

ScrollObject.reveal('.right', {
    delay: 350,
    origin: 'bottom',
    distance: '20px',
});

ScrollObject.reveal('.left', {
    delay: 250,
    origin: 'bottom',
    distance: '20px',
});

ScrollObject.reveal('.slideRight', {
    delay: 250,
    origin: 'left',
    distance: '300%',
});
