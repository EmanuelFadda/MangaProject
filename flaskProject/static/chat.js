const token = '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'
function consigliami() {
    txt = document.getElementById('testo-consiglio')
    manga = document.getElementById("advice").value

    fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        },
        body: JSON.stringify({
            "model": "gpt-3.5-turbo",
            "messages": [{ "role": "user", "content": "voglio che mi consigli 5 manga simili a " + manga + ", devi restituirmi solo i manga in un elenco puntato in html con affianco una spiegazione del perche me li consigli, non voglio nessun altro commento all'interno del messaggio" }]
        })
    }).then(response => {
        return response.json();

    }).then(data => {
        console.log(data.choices[0].message.content)
        txt.innerHTML = data.choices[0].message.content
    })
}
