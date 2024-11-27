function programm_selection(action) {
    const programm = document.getElementById("programm").value;
    window.location.assign(`/${action}?programm=${programm}`);
}
