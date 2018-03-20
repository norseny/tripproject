$('document').ready(function () {
    addFormsets()
    $(function () {
        $('input[type=datetime]').flatpickr({
            enableTime: true,
            dateFormat: "d-m-Y H:i",
            locale: "pl",
            time_24hr: true,
        });
    });
});


// $('document').ready(function(){
//     addFormsets()
//     $(function () {
//         $('input[type=datetime]').datepicker();
//     });
// });

function addFormsets() {
    const datepickerCallback = function () {
        return function (addedRow) {
            $(addedRow.find('input[type=datetime]')).flatpickr({
                enableTime: true,
                dateFormat: "d-m-Y H:i",
                locale: "pl",
                time_24hr: true,
            });
        }
    };
    $('.formset_row1').formset({
        addText: 'add new row',
        deleteText: 'remove',
        prefix: 'journey_set',
        added: datepickerCallback()
    });
    $('.formset_row2').formset({
        addText: 'add new row',
        deleteText: 'remove',
        prefix: 'accommodation_set',
        added: datepickerCallback()
    });
    $('.formset_row3').formset({
        addText: 'add new row',
        deleteText: 'remove',
        prefix: 'attraction_set',
        added: datepickerCallback()
    });
}