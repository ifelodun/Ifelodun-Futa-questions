document.addEventListener('DOMContentLoaded', () => {
    const printBtn = document.querySelector('#print-btn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }
});
