$(document).ready(function () {

    $(".download_background_query_result").on('click', function(){
        let btn_valider = $(this);
        download_url= btn_valider.data('url');
        // alert(download_url);
        // open the download link in a new tab
        window.open(download_url);
        // refresh the page
        location.reload();
    });

});