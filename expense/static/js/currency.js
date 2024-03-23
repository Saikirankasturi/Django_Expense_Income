let amount = document.getElementById("amount")
let fromCurrency = document.getElementById("from")
let toCurrency = document.getElementById("to")
let convertedAmount = document.getElementById("convertedAmount")
let convert = document.getElementById("convert")

let fromValue
let toValue
let amountValue

// for saving amount into variable
amount.addEventListener('input', getAmount)

function getAmount(e) {
  amountValue = e.target.value
}

//for saving from currency
fromCurrency.addEventListener('change', getFromCurrency)

function getFromCurrency(e) {
  fromValue = e.target.value
}

//for saving to Currency

toCurrency.addEventListener('change', getToCurrency)

function getToCurrency(e){
    toValue = e.target.value
}

convert.addEventListener('click',displayResults)

function displayResults(){
    fetch(`https://api.exchangerate-api.com/v4/latest/${fromValue}`)
    .then(currency => {
        return currency.json()
    }).then(getResults)
}

function getResults(currency)
{
  let rateCurr = currency.rates[toValue]
  let finalAnswer = rateCurr*amountValue
   convertedAmount.innerHTML=finalAnswer
}

