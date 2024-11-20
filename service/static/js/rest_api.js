$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_wishlist_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        $("#wishlist_note").val(res.note);

        if (res.is_favorite == true) {
            $("#wishlist_favorite").val("true");
        } else {
            $("#wishlist_favorite").val("false");
        }
        $("#wishlist_update").val(res.updated_time);
    }

    /// Clears all form fields
    function clear_wishlist_data() {
        $("#wishlist_name").val("");
        $("#customer_name").val("");
        $("#wishlist_favorite").val("");
        $("#wishlist_note").val("");
        $("#wishlist_update").val("");
    }

    // Updates the form with data from the response
    function update_item_data(res) {
        $("#item_id").val(res.id);
        $("#item_name").val(res.name);
        $("#item_category").val(res.category);
        $("#item_quantity").val(res.quantity);
        $("#item_price").val(res.price);

        $("#item_note").val(res.note);

        if (res.is_favorite == true) {
            $("#item_favorite").val("true");
        } else {
            $("#item_favorite").val("false");
        }
        $("#item_update").val(res.updated_time);
    }

    /// Clears all form fields
    function clear_item_data() {
        $("#item_name").val("");
        $("#customer_name").val("");
        $("#item_favorite").val("");
        $("#item_note").val("");
        $("#item_update").val("");
        $("#item_category").val("");
        $("#item_price").val("");
        $("#item_quantity").val("");
    }
    
    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // Retrieve a Wishlist
    $("#retrieve-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_wishlist_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_wishlist_data()
            flash_message(res.responseJSON.message)
        });

    });

    // Create a Wishlist
    $("#wishlist_create_btn").click(function () {

        let name = $("#wishlist_name").val();
        let note = $("#wishlist_note").val();
        let update = $("#wishlist_update").val(); 
        let is_favorite = $("#wishlist_favorite").prop("checked");
        
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify({
                name: name,
                note: note,
                updated_time: update,
                items: [],
                is_favorite: is_favorite
            })
        });

        ajax.done(function(res){
            //alert(res.toSource())
            update_wishlist_data(res)
            flash_message("Success: Create a Wishlist")
        });

        ajax.fail(function(res){
            clear_wishlist_data()
            flash_message(res.responseJSON.message)
        });

    });


    // Create an Item
    $("#item_create_btn").click(function () {

        let name = $("#item_name").val();
        let category = $("#item_category").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();
        let update = $("#item_update").val(); 
        let note = $("#item_note").val();
        let is_favorite = $("#item_favorite").prop("checked");
        let wishlist_id = $("#desired_item_wishlist").val();
    
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/wishlists/${wishlist_id}/items`,
            contentType: "application/json",
            data: JSON.stringify({
                name: name,
                category: category,
                quantity: quantity,
                price: price,
                note: note,
                updated_time: update,
                is_favorite: is_favorite
            })
        });

        ajax.done(function(res){
            //alert(res.toSource())
            update_item_data(res)
            flash_message("Success: Create an Item")
        });

        ajax.fail(function(res){
            clear_item_data()
            flash_message(res.responseJSON.message)
        });

    });
})
