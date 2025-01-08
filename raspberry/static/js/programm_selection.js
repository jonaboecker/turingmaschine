function programm_selection(action) {
    const programm = document.getElementById("program").value;
    window.location.assign(`/${action}/${programm}`);
}
