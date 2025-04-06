function addInputAlphaNumValidation(inputSelector, errorId) {
    var previousValue = ""; // Déclarer previousValue en dehors de la fonction
    $(inputSelector).on("input", function () {
        var inputValue = $(this).val();
        // var alphanumericRegex = /^[a-zA-Z0-9]*$/;
        var alphanumericRegex = /^[a-zA-Z0-9\/\-_]*$/;
        var errorMessage = $("#" + errorId);

        if (!alphanumericRegex.test(inputValue)) {
            errorMessage.css("display", "block");
            $(this).val(previousValue);
            setTimeout(function () {
                errorMessage.css("display", "none");
            }, 5000);
        } else {
            previousValue = inputValue;
            errorMessage.css("display", "none");
        }
    });
}

$(document).ready(function () {
    addInputAlphaNumValidation(".alpha_num_input", "error-message");
});