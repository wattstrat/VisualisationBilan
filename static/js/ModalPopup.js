var app = app || {};
(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define(["jQuery"], factory);
  } else if(typeof module === "object" && module.exports) {
    module.exports = factory(require("jQuery"));
  } else {
    root.LocationSearch = factory(root.jQuery);
  }
}(this, function(jQuery) {
app.ModalPopup = function(title, innerChild, footer){
    var divModal = document.createElement('div');
    divModal.className = "modal";

    var closeModal = function() {
	divModal.remove();
    }

    var divContent = document.createElement('div');
    divContent.className = "modal-content";
    divModal.appendChild(divContent);
    
    var divHeader=document.createElement('div');
    divHeader.className = "modal-header";
    var spanClose=document.createElement('span');
    spanClose.className = "close";
    spanClose.innerHTML="&times;";
    spanClose.addEventListener('click', closeModal, false)
    divHeader.appendChild(spanClose);
    if (title != null){
	
	var hTitle=document.createElement('h2');
	hTitle.innerHTML = title;
	divHeader.appendChild(hTitle);
    }    
	    
	    
    divContent.appendChild(divHeader);
    if (innerChild != null){
	var divBody=document.createElement('div');
	divBody.className = "modal-body";
	divBody.appendChild(innerChild);
	divContent.appendChild(divBody);
    }
    if (footer != null){
	var divFooter=document.createElement('div');
	divFooter.className = "modal-footer";
	divFooter.innerHTML='<h3>' + footer + '</h3>';
	divContent.appendChild(divFooter);
    }
    jQuery('body').append(divModal);
    divModal.style.display = "block";
    return divModal;
};
    var ModalPopup = app.ModalPopup;
    return ModalPopup;
}));
