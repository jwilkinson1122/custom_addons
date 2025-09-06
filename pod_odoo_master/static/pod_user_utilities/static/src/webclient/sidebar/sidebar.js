/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { UserUtilities } from "@pod_odoo_master/static/pod_user_utilities/webclient/user_utilities/user_utilities";
import { OrgContacts } from "@pod_odoo_master/static/pod_user_utilities/webclient/contacts/contacts";
import { NoteMaker } from "@pod_odoo_master/static/pod_user_utilities/webclient/note_maker/note_maker";
import { MiniCalendar } from "@pod_odoo_master/static/pod_user_utilities/webclient/calender/calender";
// import { UserUtilities } from "@pod_user_utilities/webclient/user_utilities/user_utilities";
// import { OrgContacts } from "@pod_user_utilities/webclient/contacts/contacts";
// import { NoteMaker } from "@pod_user_utilities/webclient/note_maker/note_maker";
// import { MiniCalendar } from "@pod_user_utilities/webclient/calender/calender";

export class Sidebar extends Component {
  static template = "user_utilities_sidebar";
  static components = {
    UserUtilities,
    NoteMaker,
    OrgContacts,
    MiniCalendar,
  };
  setup() {
    this.state = useState({
      todaysTasks: [],
    });
    this.orm = useService("orm");
    this.checkTodaysTasks();
  }
  async checkTodaysTasks() {
    const today = new Date().toISOString().split("T")[0];
    this.state.todaysTasks = await this.orm.search("calendar.event", [
      ["start_date", "=", today],
    ]);
  }
  showNewSidebar(contentType) {
    document.addEventListener("DOMContentLoaded", () => {
      const task = this.el.querySelector("#task");
      const note = this.el.querySelector("#note");
      const contacts = this.el.querySelector("#contacts");
      const calender = this.el.querySelector("#calender");
    });
    // Show the selected component
    if (contentType === "task") {
      note.style.display = "none";
      contacts.style.display = "none";
      calender.style.display = "none";
      // if (task.style.display === "block") {
      //   task.style.display = "block";
      // }

      if (task.style.display === "block") {
        task.style.display = "none";
      } else {
        task.style.display = "block";
      }
    } else if (contentType === "note") {
      task.style.display = "none";
      calender.style.display = "none";
      contacts.style.display = "none";
      if (note.style.display === "block") {
        note.style.display = "none";
      } else {
        note.style.display = "block";
      }
    } else if (contentType === "contacts") {
      task.style.display = "none";
      note.style.display = "none";
      calender.style.display = "none";
      if (contacts.style.display === "block") {
        contacts.style.display = "none";
      } else {
        contacts.style.display = "block";
      }
    } else if (contentType === "calender") {
      task.style.display = "none";
      contacts.style.display = "none";
      note.style.display = "none";
      if (calender.style.display === "block") {
        calender.style.display = "none";
      } else {
        calender.style.display = "block";
      }
    }
  }
  closePanel(content) {
    document.addEventListener("DOMContentLoaded", () => {
      const task = this.el.querySelector("#task");
      const note = this.el.querySelector("#note");
      const contacts = this.el.querySelector("#contacts");
      const calender = this.el.querySelector("#calender");
    });
    if (content === "task") {
      task.style.display = "none";
    }
    if (content === "note") {
      note.style.display = "none";
    }
    if (content === "contacts") {
      contacts.style.display = "none";
    }
    if (content === "calender") {
      calender.style.display = "none";
    }
  }
}
