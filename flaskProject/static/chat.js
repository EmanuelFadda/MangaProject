const token = 'sk-UIt3KbgnX9KKMfKOWYSpT'+'3BlbkFJxJ4murUVdfUr3zQ3BCX3'
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
            "messages": [{ "role": "user", "content": "voglio che mi consigli 5 manga simili a " + manga + ", devi restituirmi solo i manga in un elenco creato con i tag html <ul> e <li> in html con affianco una spiegazione del perche me li consigli, non voglio nessun altro commento all'interno del messaggio" }]
        })
    }).then(response => {
        
        
        return  data= response.json();
        //ritorna un oggetto object promise, pere renderlo utilizzabile è necessario un altro then
    }).then(data => {
        console.log(data)
        txt.innerHTML = data.choices[0].message.content
        document.getElementById("wait").style.display="none"
    })
}
