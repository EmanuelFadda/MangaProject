const token = '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'
function consigliami() {
    txt = document.getElementById('testo-consiglio')
    manga = document.getElementById("advice").value
    document.getElementById("wait").style.display="block"
    fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        },
        body: JSON.stringify({
            "model": "gpt-3.5-turbo",
            "messages": [{ "role": "user", "content": "voglio che mi consigli 5 manga simili a " + manga + ", devi restituirmi solo i manga in un elenco formato da tag in html con affianco una spiegazione del perche me li consigli, non voglio nessun altro commento all'interno del messaggio" }]
        })
    }).then(response => {
        return response.json();

    }).then(data => {
        console.log(data.choices[0].message.content)
        txt.innerHTML = data.choices[0].message.content
        document.getElementById("wait").style.display="none"
    })
}
