/** @odoo-module */

import { Dialog } from "@web/core/dialog/dialog"
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";

/**
 * Add webcam in image field
 * https://developer.mozilla.org/en-US/docs/Web/API/Media_Capture_and_Streams_API/Taking_still_photos
 */

export class WebcamDialog extends Component {
    static template = "oehealth.WebcamDialog";

    static components = {
        Dialog,
    };

    static props = {
        record: Object,
        field: String,
        title: String,
        close: Function,
    };


    setup() {

        this.state = useState({'image': false});
        this.video = useRef('video');
        this.image = useRef('image');

        // play video
        onMounted(async () => {
            this.video.el.srcObject = await navigator.mediaDevices.getUserMedia({ video: true });
            this.video.el.play();
        })

        // stop video
        onWillUnmount(async () => {
            this.stopWebcam();
        })
    }

    captureImage() {
        let video = this.video.el;
        let image = this.image.el;

        // take image
        let canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        image.src = canvas.toDataURL('image/png');
        this.state.image = image.src;

        // hide video then show image
        // odoo use bootstrap css
        video.classList.add('d-none');
        image.classList.remove('d-none');
        this._addFlashEffect();
    }

    recaptureImage() {
        this.state.image = false;
        // hide image then show video
        this.video.el.classList.remove('d-none');
        this.image.el.classList.add('d-none');
    }

    stopWebcam(){
        this.video.el.srcObject.getTracks().forEach(track => track.stop());
        this.props.close();
    }

    async confirm() {
        if (this.state.image){
            await this.props.record.update({ [this.props.field]: this.state.image.split(',')[1]})
        }

        this.stopWebcam()
    }

    _addFlashEffect() {
        this.image.el.classList.add('flash-effect');
        setTimeout(() => {
            this.image.el.classList.remove('flash-effect');
        }, 500);
    }

}