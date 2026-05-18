import { registry } from "@web/core/registry";
import { Component,useState } from "@odoo/owl";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { rpc } from "@web/core/network/rpc";

class VoiceRecorderWidget extends Component {
    static template = "oehealth_claims.VoiceRecorderWidget";
    static props = {
        ...standardWidgetProps,
    };

    setup() {
        this.state = useState({
            recording: false,
            elapsed: "00:00",
        });

        this.mediaRecorder = null;
        this.chunks = [];
        this.timer = null;
        this.startTime = null;
    }

    async toggleRecording() {
        if (this.state.recording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }


    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.chunks = [];

            this.mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    this.chunks.push(e.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                const blob = new Blob(this.chunks, { type: "audio/webm" });
                await this.sendVoiceMessageToChatter(blob);


                const url = URL.createObjectURL(blob);
                console.log(123123, url)
//                this.downloadFile(url);
            };

            this.mediaRecorder.start();
            this.state.recording = true;

            // Timer for elapsed time
            this.startTime = Date.now();
            this.timer = setInterval(() => {
                const diff = Math.floor((Date.now() - this.startTime) / 1000);
                const minutes = String(Math.floor(diff / 60)).padStart(2, "0");
                const seconds = String(diff % 60).padStart(2, "0");
                this.state.elapsed = `${minutes}:${seconds}`;
            }, 1000);

        } catch (err) {
            console.error("Microphone access denied:", err);
            alert(_t("Microphone access denied!"));
        }
    }

    stopRecording() {
        if (this.mediaRecorder) {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach((t) => t.stop());
        }
        this.state.recording = false;
        clearInterval(this.timer);
        this.state.elapsed = "00:00";
    }

    async blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64data = reader.result.split(",")[1]; // remove "data:audio/webm;base64,"
                resolve(base64data);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }


    async sendVoiceMessageToChatter(blob) {
        const base64 = await this.blobToBase64(blob);
        const filename = `Voice-${Date.now()}.webm`;
         await this.env.services.orm.call(
            "ir.attachment",
            "create",
            [{
                name: filename,
                datas: base64,
                res_model: this.props.record.resModel,  // model to link to
                res_id: this.props.record.resId,       // record ID to link to
                mimetype: "audio/webm",
            }]
        );
    }

//    downloadFile(url) {
//        const a = document.createElement("a");
//        a.style.display = "none";
//        a.href = url;
//        a.download = `Voice-${Date.now()}.webm`;
//        document.body.appendChild(a);
//        a.click();
//        window.URL.revokeObjectURL(url);
//    }
}

export const voiceRecorderWidget = {
    component: VoiceRecorderWidget,
    extractProps: ({ attrs }) => ({}),
    supportedAttributes: [],
};

registry.category("view_widgets").add("web_voice_recorder", voiceRecorderWidget);