import io
import pandas as pd
import base64

def get_download_link(df, filename=None, original_file_type=None):
    if not original_file_type:
        original_file_type = ".csv"
    
    if not filename:
        filename = f"cleaned_data{original_file_type}"
    
    buffer = io.BytesIO()
    
    if original_file_type.lower() in ['.xlsx', '.xls']:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Cleaned Data')
            worksheet = writer.sheets['Cleaned Data']
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_width)
        
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        df.to_csv(buffer, index=False)
        mimetype = 'text/csv'
    
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    
    href = f'<a href="data:{mimetype};base64,{b64}" download="{filename}">Download Cleaned Data ({original_file_type[1:].upper()})</a>'
    return href
