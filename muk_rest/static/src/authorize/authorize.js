/** @odoo-module **/

const { whenReady } = owl;

await whenReady();

const popoverTriggerList = [].slice.call(
	document.querySelectorAll('[data-bs-toggle="popover"]')
);

popoverTriggerList.map((el) => {
	let opts = {
		animation: false,
	}
	if (el.hasAttribute('data-bs-content-id')) {
		opts.content = (
			document.getElementById(
				el.getAttribute('data-bs-content-id')
			).innerHTML
		);
	    opts.html = true;
	}
	new Popover(el, opts);
});
