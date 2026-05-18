import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";
import { FsmTaskCalendarModel } from "@industry_fsm/views/fsm_task_calendar/fsm_calendar_model";
import { intersection } from "@web/core/utils/arrays";

const STORAGE_KEY = "fs_cal_filter_state_v2";

patch(FsmTaskCalendarModel.prototype, {

    setup() {
        super.setup(...arguments);
        this.filterStorageKey = STORAGE_KEY;
    },

    async updateFilters(fieldName, filters, active) {
        filters.forEach(f => { f.active = active; });

        const snapshot = {};
        for (const [sec, info] of Object.entries(this.data.filterSections)) {
            snapshot[sec] = {};
            for (const f of info.filters) {
                snapshot[sec][f.value] = f.active;
            }
        }

        try {
            browser.localStorage.setItem(this.filterStorageKey, JSON.stringify(snapshot));
        } catch (err) {
            console.warn("FSM: could not persist filter state", err);
        }

        await super.updateFilters(...arguments);
    },

    async loadDynamicFilters(data, dynamicFiltersInfo) {
        const sections = await super.loadDynamicFilters(...arguments);

        let saved = null;
        const raw = browser.localStorage.getItem(this.filterStorageKey);
        if (raw) {
            try {
                saved = JSON.parse(raw);
            } catch (_) {
            }
        }

        for (const [secName, sec] of Object.entries(sections)) {
            for (const filter of sec.filters) {
                const hadState = saved && saved[secName] && saved[secName][filter.value] !== undefined;
                filter.active = hadState ? saved[secName][filter.value] : false;
            }
        }

        return sections;
    },

    async loadRecords(data) {
        const fetched = await super.loadRecords(data);
        this._cachedRecords = { ...fetched };
        return fetched;
    },

    async updateData(data) {
        await super.updateData(data);

        data.records = { ...this._cachedRecords };

        for (const [field, section] of Object.entries(data.filterSections)) {
            const isRelational = this.meta.filtersInfo[field]?.writeResModel;
            if (isRelational) continue;

            const activeOnes = section.filters.filter(f => f.active);
            if (!activeOnes.length) continue;

            const fieldMeta = this.meta.fields[field];
            if (!fieldMeta) continue;

            const hiddenVals = section.filters.filter(f => !f.active);

            for (const [id, rec] of Object.entries(data.records)) {
                const raw = rec.rawRecord[field];
                let shouldDrop = false;

                if (["many2many", "one2many"].includes(fieldMeta.type)) {
                    const hiddenSet = hiddenVals.map(f => f.value);
                    shouldDrop = raw ? intersection(raw, hiddenSet).length === raw.length : true;
                } else {
                    const val = Array.isArray(raw) ? raw[0] : raw;
                    shouldDrop = val ? hiddenVals.some(f => f.value === val) : true;
                }
                if (shouldDrop) {
                    delete data.records[id];
                }
            }
        }

        if (this.aggregate) {
            for (const [field, { filters }] of Object.entries(data.filterSections)) {
                const counts = this.computeAggregatedValues(field, data);
                for (const f of filters) {
                    f.aggregatedValue = counts[f.value] ?? 0;
                }
            }
        }
    },
});