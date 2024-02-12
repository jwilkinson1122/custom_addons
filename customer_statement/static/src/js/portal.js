$(document).ready(function (e) {
    var start_date = $('#start_date').val();
    var end_date = $('#end_date').val();
	$("#send_cust_btn").on("click", function () {
		$.ajax({
            url: "/my/customer_statements/send",
            data: {'customer_send_statement':true},
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                if (datas.msg){
                	alert(datas.msg);
                }
            },
        });
	});
	$("#send_cust_due_btn").on("click", function () {
		$.ajax({
            url: "/my/customer_statements/send",
            data: {'customer_send_overdue_statement':true},
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                if (datas.msg){
                	alert(datas.msg);
                }
            },
        });
	});
    $("#filter_send_cust_btn").on("click", function () {
		$.ajax({
            url: "/my/customer_statements/send",
            data: {'customer_send_filter_statement':true},
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                if (datas.msg){
                	alert(datas.msg);
                }
            },
        });
	});
    $('#start_date').on("change",function(){
        selected_start_date = $('#start_date').val();
        selected_end_date = $('#end_date').val();
        if (new Date(selected_start_date) > new Date(selected_end_date)){
            alert('Date from should be less than or equal Date to');
            $('#start_date').val(start_date);
            $('#end_date').val(end_date);
        }
        else if(new Date(selected_end_date) < new Date(selected_start_date)){
            alert('Date to should be greater than or equal Date from');
            $('#start_date').val(start_date);
            $('#end_date').val(end_date);
        }
    });
    $('#end_date').on("change",function(){
        selected_start_date = $('#start_date').val();
        selected_end_date = $('#end_date').val();
        if (new Date(selected_start_date) > new Date(selected_end_date)){
            alert('Date from should be less than or equal Date to');
            $('#start_date').val(start_date);
            $('#end_date').val(end_date);
        }
        else if(new Date(selected_end_date) < new Date(selected_start_date)){
            alert('Date to should be greater than or equal Date from');
            $('#start_date').val(start_date);
            $('#end_date').val(end_date);
        }
    });
    $("#filter_get_statement").on("click", function () {
		$.ajax({
            url: "/my/customer_statements/get",
            data: {'start_date':$('#start_date').val(),'end_date':$('#end_date').val()},
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                location.reload(true);
            },
        });
	});
});