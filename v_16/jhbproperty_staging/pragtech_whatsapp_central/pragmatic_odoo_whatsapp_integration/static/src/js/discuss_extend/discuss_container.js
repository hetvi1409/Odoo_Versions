/** @odoo-module **/

import { DiscussContainer } from '@mail/components/discuss_container/discuss_container';

const DiscussContainerMod = DiscussContainer.extend({
    _willDestroy() {
        if (this.discuss && DiscussContainer.currentInstance === this) {
            console.log("closing discuss");
            // this.discuss.close();
        }
    }
})

// export default DiscussContainerMod;
return DiscussContainerMod;
