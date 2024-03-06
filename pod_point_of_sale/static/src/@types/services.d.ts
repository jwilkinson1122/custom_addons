declare module "services" {
    import { barcodeReaderService } from "@pod_point_of_sale/app/barcode/barcode_reader_service";
    import { debugService } from "@pod_point_of_sale/app/debug/debug_service";
    import { hardwareProxyService } from "@pod_point_of_sale/app/hardware_proxy/hardware_proxy_service";
    import { popupService } from "@pod_point_of_sale/app/popup/popup_service";
    import { numberBufferService } from "@pod_point_of_sale/app/utils/number_buffer_service";
    import { notificationService } from "@pod_point_of_sale/app/notification/notification_service";
    import { posBusService } from "@pod_point_of_sale/app/bus/pos_bus_service";
    import { customerDisplayService } from "@pod_point_of_sale/app/customer_display/customer_display_service";
    import { reportService } from "@pod_point_of_sale/app/utils/report_service";
    import { soundService } from "@pod_point_of_sale/app/sound/sound_service";

    export interface Services {
        barcode_reader: Resolved<ReturnType<typeof barcodeReaderService.start>>;
        debug: ReturnType<typeof barcodeReaderService.start>;
        hardware_proxy: ReturnType<typeof hardwareProxyService.start>;
        popup: ReturnType<typeof popupService.start>;
        number_buffer: ReturnType<typeof numberBufferService.start>;
        pos_notification: ReturnType<typeof notificationService.start>;
        pos_bus: ReturnType<typeof posBusService.start>;
        customer_display: ReturnType<typeof customerDisplayService.start>;
        report: ReturnType<typeof reportService.start>;
        sound: ReturnType<typeof soundService.start>;
    }
}
