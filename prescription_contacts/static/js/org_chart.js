/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component,useRef,useState,onMounted } = owl;
export class PartnerOrgChart extends Component {
    static template = 'res_org_chart_partner'
    setup(){
        super.setup();
        this.state = useState({
            data: {
                parent: {},
                child: [],
            },
        });
        this.orm = useService("orm")
        this.actionService = useService("action");
        this.partner_id = null;
        onMounted(async()=> {
            await this.fetchPartnerData()
        })
   }

   async fetchPartnerData(){
        this.partner_id = this.env.model.__bm_load_params__.res_id
        var response = await this.orm.call('res.partner', 'fetch_data',[this.partner_id]);
        this.state.data['parent'] = response['parent'];
        this.state.data['child'] = response['child'];
   }
   async redirectToCostObject(ObjectId) {
        const action = await this.orm.call('res.partner', 'get_formview_action', [ObjectId]);
        this.actionService.doAction(action);

    }
}
registry.category("fields").add("partner_org_chart", PartnerOrgChart);