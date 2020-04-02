$(document).ready(function(){

  var searchForm =$(".search-form")
  var registerForm =$(".register-form")
  var registerFormMethod= registerForm.attr("method")
  var registerFormEndpoint= registerForm.attr("action")
  var loginForm =$(".login-form")
  var loginFormMethod= loginForm.attr("method")
  var loginFormEndPoint= loginForm.attr("action")
  var contactForm = $(".contact-form")
  var contactFormMethod = contactForm.attr("method")
  var contactFormEndpoint = contactForm.attr("action")
  var guestForm=$(".guest-form")
  

  function displaySubmitting(submitBtn, defaultText, doSubmit){
    if (doSubmit){
      submitBtn.addClass("disabled")
      submitBtn.html("<div class='spinner-border spinner-border-sm' role='status'></div> Submitting...")
    } else {
      submitBtn.removeClass("disabled")
      submitBtn.html(defaultText)
    }

  }

  searchForm.submit(function(event){
    var searchFormBtn=searchForm.find("[type='submit']")
    var searchFormBtnTxt=searchFormBtn.text()
    var searchFormMethod=searchForm.attr("method")
    var searchFormEndPoint=searchForm.attr("action")
    var searchFormData=searchForm.serialize()
    var thisForm=$(this)
    displaySubmitting(searchFormBtn,"",true)

    $.ajax({
      method:searchFormMethod,
      url:searchFormEndPoint,
      data:searchFormData,
      success: function(data){
        setTimeout(function(){
          displaySubmitting(searchFormBtn,searchFormBtnTxt,false)
        }, 500)
      }
    })
  })

  contactForm.submit(function(event){
    event.preventDefault()
    var contactFormSubmitBtn = contactForm.find("[type='submit']")
    var contactFormSubmitBtnTxt = contactFormSubmitBtn.text()
    var contactFormData = contactForm.serialize()
    var thisForm = $(this)
    displaySubmitting(contactFormSubmitBtn, "", true)
    $.ajax({
      method: contactFormMethod,
      url:  contactFormEndpoint,
      data: contactFormData,
      success: function(data){
        contactForm[0].reset()
        $.alert({
          title: "Success!",
          content: data.message,
          theme: "material",
        })
        setTimeout(function(){
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)
        }, 500)
      },
      error: function(error){
        console.log(error.responseJSON)
        var jsonData = error.responseJSON
        var msg = ""
        $.each(jsonData, function(key, value){ // key, value  array index / object
          msg += key + ": " + value[0].message + "<br/>"
        })
        $.alert({
          title: "Oops!",
          content: msg,
          theme: "material",
        })
        setTimeout(function(){
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)
        }, 500)
      }
    })
  })

  registerForm.submit(function(event){
    event.preventDefault()
    var registerFormSubmitBtn=registerForm.find("[type='submit']")
    var registerFormSubmitBtnTxt=registerFormSubmitBtn.text()
    var registerFormData=registerForm.serialize()
    var thisForm=$(this)
    displaySubmitting(registerFormSubmitBtn,"",true)
    $.ajax({
      method:registerFormMethod,
      url:registerFormEndpoint,
      data:registerFormData,
      type:"POST",
      success: function(data){
        registerForm[0].reset()
        window.location.href="/otp/"
        setTimeout(function(){
          displaySubmitting(registerFormSubmitBtn,registerFormSubmitBtnTxt,false)
        },500)
      },
      error: function(error){
        var jsonData = error.responseJSON
        var msg=""
        for (var key in jsonData){
          msg+=jsonData[key]+"<br />"
        }
        $.alert({
          title: "Oops!",
          content: msg,
          theme: "material",
        })
        setTimeout(function(){
          displaySubmitting(registerFormSubmitBtn,registerFormSubmitBtnTxt,false)
        }, 500)
      }
    })
  })

  loginForm.submit(function(event){
    event.preventDefault()
    var loginFormSubmitBtn=loginForm.find("[type='submit']")
    var nextURL=loginForm.find("[id='nextURL']").val()
    var loginFormSubmitBtnTxt=loginFormSubmitBtn.text()
    var loginFormData=loginForm.serialize()
    var thisForm=$(this)
    displaySubmitting(loginFormSubmitBtn,"",true)
    $.ajax({
      method:loginFormMethod,
      url:loginFormEndPoint,
      data:loginFormData,
      success: function(data){
        loginForm[0].reset()
        setTimeout(function(){
          displaySubmitting(loginFormSubmitBtn,loginFormSubmitBtnTxt,false)
        },500)
        // if(loginFormEndPoint!="")
        //   window.location.href="/cart/checkout/"
        // else
        //   window.location.href="/"
        window.location.href=nextURL

      },
      error: function(error){
        var jsonData = error.responseJSON 
        var msg=""
        for (var key in jsonData){
          msg+=jsonData[key]+"<br />"
        }
        $.alert({
          title: "Oops!",
          content: msg,
          theme: "material",
        })
        setTimeout(function(){
          displaySubmitting(loginFormSubmitBtn,loginFormSubmitBtnTxt,false)
        }, 500)
      }
    })
  })

  var productForm=$(".form-product-ajax")
  productForm.submit(function(event){
    event.preventDefault();
    var thisForm=$(this)
    var actionEndpoint=thisForm.attr("data-endpoint");
    var httpMethod=thisForm.attr("method");
    var formData=thisForm.serialize();

    $.ajax({
      url:actionEndpoint,
      method:httpMethod,
      data:formData,
      success: function(data){
        var submitSpan=thisForm.find("#submit-span")
        if (data.added) {
          submitSpan.html("<button type='submit' class='btn btn-danger mt-2'>Remove from Cart</button>")
        } else {
          submitSpan.html("<button type='submit' class='btn btn-success mt-2'>Add to Cart</button>")
        }
        var navbarCount=$("#navbar-cart-count")
        navbarCount.text(data.cartItemCount)
        var currentPath = window.location.href
        if (currentPath.indexOf("cart") != -1){
          refreshCart()
        }
      },
      error: function(errorData){
        console.log(errorData)
        $.alert({
          theme:'material',
          title:'Oops!',
          content:"An Error Occured",
        })
        console.log(errorData)
      }
    })
  })
  function refreshCart(){
    var cartTable=$("#cart-table")
    var cartBody=cartTable.find("#cart-body")
    var productRows=cartBody.find("#cart-products")
    var currentUrl=window.location.href
    var refreshCartUrl='/api/cart/';
    var refreshCartMethod="GET";
    var data={};
    $.ajax({
      url:refreshCartUrl,
      method:refreshCartMethod,
      data:data,
      success: function(data){
        if (data.products.length <= 0){
          window.location.href=currentUrl
        }
        else{
          window.location.href=currentUrl
        }
      },
      error: function(errorData){
        $.alert({
          theme:'material',
          title:'Oops!',
          content:"An Error Occured",
        })
        console.log(errorData)
      }
    })

  }
})
