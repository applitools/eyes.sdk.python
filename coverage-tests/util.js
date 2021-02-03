function capitalizeFirstLetter(string) {
    return string.toString().charAt(0).toUpperCase() + string.toString().slice(1);
}
module.exports = {
    capitalizeFirstLetter: capitalizeFirstLetter,
}
