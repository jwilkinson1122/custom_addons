/** @odoo-module **/
import {registry} from "@web/core/registry";
import {Layout} from "@web/search/layout";
import {getDefaultConfig} from "@web/views/view";
import {useService} from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import {Domain} from "@web/core/domain";
import {sprintf} from "@web/core/utils/strings";

const {Component, useSubEnv, useState, onMounted, onWillStart, useRef} = owl;
import {loadJS, loadCSS} from "@web/core/assets"

class OrthoticRepairDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            repairOrderStats: {'total_repair_orders': 0, 'assign_to_technician': 0, 'orthotic_inspection_mode': 0, 'in_progress_orders': 0, 'review_orders': 0, 'complete_orders': 0, 'cancel_orders': 0},
            repairOrders: {'x-axis': [], 'y-axis': []},
            repairOrderByMonth: {'x-axis': [], 'y-axis': []},
            invoiceStatus: {'x-axis': [], 'y-axis': []},
            repairServices: {'x-axis': [], 'y-axis': []},
            orthoticRepairDurations: {'data': []},
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        this.repairOrders = useRef('orthotic_repair_order_details');
        this.repairOrderByMonth = useRef('orthotic_sale_orders');
        this.invoiceStatus = useRef('invoice_status_details');
        this.repairServices = useRef('repair_service_details');
        this.orthoticRepairDurations = useRef('repair_time_duration');


        onWillStart( async () => {
            await loadJS('/pod_orthotic_repair/static/src/js/lib/moment.min.js');
            await loadJS('/pod_orthotic_repair/static/src/js/lib/apexcharts.js');
            let repairOrderData = await this.orm.call('orthotic.repair.dashboard', 'get_orthotic_repair_dashboard', []);
            if(repairOrderData){
                this.state.repairOrderStats = repairOrderData;
                this.state.repairOrders = {'x-axis': repairOrderData['repair_orders_details'][0], 'y-axis': repairOrderData['repair_orders_details'][1]}
                this.state.repairOrderByMonth = {'x-axis': repairOrderData['repair_order_month'][0], 'y-axis': repairOrderData['repair_order_month'][1]}
                this.state.invoiceStatus = {'x-axis': repairOrderData['invoice_status'][0], 'y-axis': repairOrderData['invoice_status'][1]}
                this.state.repairServices = {'x-axis': repairOrderData['top_five_repair_services'][0], 'y-axis': repairOrderData['top_five_repair_services'][1]}
                this.state.orthoticRepairDurations = {'data': repairOrderData['orthotic_repair_duration']}
            }
        });
        onMounted(() => {
            this.renderRepairOrdersGraph();
            this.renderRepairOrderByMonthGraph();
            this.renderInvoiceStatusGraph();
            this.renderRepairServiceGraph();
            this.renderRepairDurationGraph();
        })
    }

    viewRepairOrders(status){
        let domain,context;
        let order = this.getRepairOrders(status);
        if (status === 'all'){
            domain = []
        }else {
            domain = [['stages', '=', status]]
        }
        context = { 'create':false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: order,
            res_model: 'orthotic.repair.order',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'calendar'], [false, 'pivot'], [false, 'graph'], [false, 'activity']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getRepairOrders(status){
        let order;
        if(status === 'all'){
            order = 'Repair Orders'
        }else if(status === 'assign_to_technician') {
            order = 'Assign to Technician'
        } else if(status === 'inspection_mode') {
            order = 'Inspection Mode'
        } else if(status === 'in_progress') {
            order = 'In Progress'
        }else if(status === 'review') {
            order = 'Review Orders'
        }else if(status === 'complete') {
            order = 'Complete Orders'
        }else if(status === 'cancel') {
            order = 'Cancel Orders'
        }
        return order;
    }

    renderGraph(el, options){
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

    renderRepairOrdersGraph(){
        const options = {
            series: [{
                name: 'Status',
                data: this.state.repairOrders['y-axis'],
            }],
            chart: {
                height: 400,
                type: 'bar',
            },
            colors: ['#f29e4c', '#f1c453', '#efea5a',  '#b9e769',  '#83e377', '#16db93', '#0db39e', '#048ba8', '#2c699a', '#54478c'],
            plotOptions: {
                bar: {
                    columnWidth: '10%',
                    distributed: true,
                }
            },
            dataLabels: {
                enabled: false
            },
            legend: {
                show: false
            },
            xaxis: {
                categories: this.state.repairOrders['x-axis'],
                labels: {
                    style: {
                        colors: ['#000000'],
                        fontSize: '13px'}
                }
            }
        };
        this.renderGraph(this.repairOrders.el, options);
    }

    renderRepairOrderByMonthGraph (){
        const options = {
            series: [{
                name: 'Status',
                data: this.state.repairOrderByMonth['y-axis'],
            }],
            chart: {
                height: 400,
                type: 'bar',
            },
            colors: ['#f29e4c', '#f1c453', '#efea5a',  '#b9e769',  '#83e377', '#16db93', '#0db39e', '#048ba8', '#2c699a', '#54478c'],
            plotOptions: {
                bar: {
                    columnWidth: '10%',
                    distributed: true,
                }
            },
            dataLabels: {
                enabled: false
            },
            legend: {
                show: false
            },
            yaxis: {
                labels: {
                    formatter: function (val) {
                        return val.toFixed(0);
                    }
                },
            },
            xaxis: {
                categories: this.state.repairOrderByMonth['x-axis'],
                labels: {
                    style: {
                        colors: ['#000000'],
                        fontSize: '13px'
                    }
                }
            }
        };
        this.renderGraph(this.repairOrderByMonth.el, options);
    }

    renderInvoiceStatusGraph(){
        const options = {
            series: this.state.invoiceStatus['y-axis'],
            chart: {
                type: 'pie',
                height: 410
            },
            colors: ['#008000', '#D80032'],
            dataLabels: {
                enabled: false
            },
            labels: this.state.invoiceStatus['x-axis'],
            legend: {
                position: 'bottom',
            },
        };
        this.renderGraph(this.invoiceStatus.el, options);
    }

    renderRepairServiceGraph(){
        const options = {
            series: this.state.repairServices['y-axis'],
            chart: {
                type: 'donut',
                height: 410
            },
            colors: ['#16db93', '#83e377', '#b9e769', '#efea5a', '#f1c453', '#f29e4c'],
            dataLabels: {
                enabled: false
            },
            labels: this.state.repairServices['x-axis'],
            legend: {
                position: 'bottom',
            },
        };
        this.renderGraph(this.repairServices.el, options);
    }

    renderRepairDurationGraph(){
        let repair_data = []
        let data = this.state.orthoticRepairDurations['data']
            for (const ss of data) {
                repair_data.push({
                    'name': ss['orthotic_problem'],
                    'data': [{
                        'x': 'Repair Durations',
                        'y': [ new Date(ss['receiving_date']).getTime(), new Date(ss['delivery_date']).getTime()]
                    }]
                })
            }
            const options = {
                series: repair_data,
                chart: {
                    height: 350,
                    type: 'rangeBar'
                },
                plotOptions: {
                    bar: {
                        horizontal: true
                    }
                },
                dataLabels: {
                    enabled: true,
                    formatter: function(val) {
                        var a = moment(val[0])
                        var b = moment(val[1])
                        var diff = b.diff(a, 'days')
                        return diff + (diff > 1 ? ' days' : ' day')
                    }
                },
                fill: {
                    type: 'gradient',
                    gradient: {
                        shade: 'light',
                        type: 'vertical',
                        shadeIntensity: 0.25,
                        gradientToColors: undefined,
                        inverseColors: true,
                        opacityFrom: 1,
                        opacityTo: 1,
                        stops: [50, 0, 100, 100]
                    }
                },
                xaxis: {
                    type: 'datetime'
                },
                legend: {
                    position: 'bottom'
                }
        };
        this.renderGraph(this.orthoticRepairDurations.el, options);
    }
}
OrthoticRepairDashboard.template = "pod_orthotic_repair.orthotic_dashboard";
registry.category("actions").add("orthotic_repair_dashboard", OrthoticRepairDashboard);