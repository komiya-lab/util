# utilities for Komiya-lab

## chj2json.py
CHJのデータファイルをJSONL形式(1行1Json)に変換するスクリプトです。
句点登場時とサンプルIDの変化時に、各行の語を結合して文単位でJson化します。
データは以下の形式です
```json
{
    "sentence": "コーパスに現れた文", 
    "sentence_normalize": "語を標準形に直した文", 
    "tokens": [
        {
            "開始位置" : "",
            "連番": "",
            "コア": "",
            "書字形出現形": "",
            ... (tokenの要素) 
        }
    ]
    ... 他メタ情報
}
```
