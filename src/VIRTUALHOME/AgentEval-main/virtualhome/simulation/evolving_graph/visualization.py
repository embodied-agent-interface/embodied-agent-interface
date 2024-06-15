import matplotlib.pyplot as plt

def error_draw_chart(data, file_path, number_font_size=6, rotation=45, divide_k=None):
    if divide_k is not None:
        # Divide the data into k parts
        for i in range(divide_k):
            lower = i * len(data) // divide_k
            upper = (i + 1) * len(data) // divide_k
            if upper > len(data):
                upper = len(data)
            sub_data = {}
            for j in range(lower, upper):
                sub_data[list(data.keys())[j]] = data[list(data.keys())[j]]
            error_draw_chart(sub_data, file_path.replace('.png', f'_{i}.png'), number_font_size, rotation)
    
    labels = list(data.keys())
    x = range(len(labels))
    TP = [v[0] for v in data.values()]
    FP = [v[1] for v in data.values()]
    FN = [v[2] for v in data.values()]
    precision = [v[3] for v in data.values()]
    recall = [v[4] for v in data.values()]
    f1 = [v[5] for v in data.values()]
    bar_width = 0.25
    r1 = [i - bar_width for i in x]
    r2 = x
    r3 = [i + bar_width for i in x]

    plt.bar(r1, precision, width=bar_width, color='lightblue', label='Precision')
    plt.bar(r2, recall, width=bar_width, color='blue', label='Recall')
    plt.bar(r3, f1, width=bar_width, color='darkblue', label='F1')
    
    for i in range(len(labels)):
        plt.text(r1[i], precision[i], f'{TP[i]+FP[i]}', ha='center', fontsize=number_font_size)
        plt.text(r2[i], recall[i], f'{TP[i]+FN[i]}', ha='center', fontsize=number_font_size)
        # plt.text(r3[i], f1[i], f'{int(totals[i] * f1[i])}', ha='center', fontsize=number_font_size)
    
    plt.xticks(x, labels, rotation=rotation, fontsize=number_font_size)
    plt.xlabel('Error Type')
    plt.ylabel('Rates')
    plt.title('Error Analysis')
    plt.legend()
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close() 

def draw_bar_chart(data, file_path, number_font_size=6, rotation=45, divide_k=None):
    if divide_k is not None:
        # Divide the data into k parts
        for i in range(divide_k):
            lower = i * len(data) // divide_k
            upper = (i + 1) * len(data) // divide_k
            if upper > len(data):
                upper = len(data)
            sub_data = {}
            for j in range(lower, upper):
                sub_data[list(data.keys())[j]] = data[list(data.keys())[j]]
            draw_bar_chart(sub_data, file_path.replace('.png', f'_{i}.png'), number_font_size, rotation)
    
    labels = list(data.keys())
    x = range(len(labels))
    precond_scores = [v[0] for v in data.values()]
    effect_scores = [v[1] for v in data.values()]
    totals = [v[2] for v in data.values()]
    bar_width = 0.35
    r1 = [i - bar_width / 2 for i in x]
    r2 = [i + bar_width / 2 for i in x]

    plt.bar(r1, precond_scores, width=bar_width, color='lightblue', label='Precond Score')
    plt.bar(r2, effect_scores, width=bar_width, color='darkblue', label='Effect Score')
    
    for i in range(len(labels)):
        mid_point = (r1[i] + r2[i]) / 2
        plt.text(mid_point, max(precond_scores[i], effect_scores[i]), f'{totals[i]}', ha='center', va='bottom', fontsize=number_font_size)
        
    plt.xticks(x, labels, rotation=rotation, fontsize=number_font_size)
    plt.xlabel('Error Type')
    plt.ylabel('Scores')
    plt.title('Error Type Analysis')
    plt.legend()
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
