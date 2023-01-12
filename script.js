
function orderRows(comparator) {
    const body = document.querySelector('tbody');
    rows = [...body.querySelectorAll('tr')]
    rows.sort(comparator)
    body.replaceChildren(...rows)
}

function _parseFloat(s) {
    let result = parseFloat(s)
    if (!isNaN(result))
        return result
    return parseFloat(s.replace(/\D/g, ''))
}

for (let th of document.querySelectorAll('th')) {
    console.log(th.parentElement)
    th.onclick = () => {
        const index = [...th.parentElement.children].indexOf(th)
        console.log('clicked: ', index, th)
        const comparator = (trL, trR) => {
            const l = trL.children[index].innerText
            const r = trR.children[index].innerText
            let lfloat = _parseFloat(l)
            let rfloat = _parseFloat(r)
            if (!isNaN(lfloat) && !isNaN(rfloat))
                return lfloat < rfloat ? -1 : 1
            else
                return l < r ? -1 : 1
        }
        orderRows(comparator)
    }
}