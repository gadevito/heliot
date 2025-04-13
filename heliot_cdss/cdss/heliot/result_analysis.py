import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

all_timings = []
def clean_labels(text):
    """Clean and standardize labels"""
    if pd.isna(text):
        return "UNKNOWN"
    return text.strip().upper()

def clean_reaction_types(row):
    """Clean and standardize reaction types"""
    if row['classification_descr'] == "DRUG CLASS CROSS-REACTIVITY WITH DOCUMENTED TOLERANCE":
        return "None"
    
    reaction = row['reaction_types']
    if pd.isna(reaction):
        return "None"
    return str(reaction).strip().upper()


def create_confusion_matrix_class_plot(y_true, y_pred, labels, output_file):
    """Create and save the confusion matrix plot"""
    # Convert labels to all lower-case and first letter in upper-case
    formatted_labels = [label.capitalize() for label in labels]
    
    plt.figure(figsize=(12, 8))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    # Use labels to format display 
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=formatted_labels, yticklabels=formatted_labels)
    
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    
    # Oblique x labels
    plt.xticks(rotation=45, ha='right')
    # Horizontal y labels
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def calculate_class_metrics(y_true, y_pred, labels):
    """Calculate per-class metrics"""
    class_metrics = {}
    for label in labels:
        y_true_binary = (y_true == label)
        y_pred_binary = (y_pred == label)
        
        class_metrics[label] = {
            'Precision': precision_score(y_true_binary, y_pred_binary),
            'Recall': recall_score(y_true_binary, y_pred_binary),
            'F1': f1_score(y_true_binary, y_pred_binary)
        }
    return class_metrics

def main(iter):
    print("Loading results...")
    try:
        df = pd.read_excel(f'./results/{iter}/results_full_synth.xlsx', dtype={'drug_code': str, 'leaflet': str, 'patient_id': str, 'classification':str})  
    except Exception as e:
        print(f"Error while loading the results: {str(e)}")
        return

    print("\nPreparing data...")
    all_timings.extend(df['timing'].dropna().tolist())

    df['true_labels'] = df['classification_descr'].apply(clean_labels)
    df['pred_labels'] = df['classification_resp'].apply(clean_labels)
    
    df['true_reactions'] = df.apply(clean_reaction_types, axis=1)
    df['pred_reactions'] = df['reaction_resp'].apply(lambda x: "None" if pd.isna(x) else str(x).strip().upper())

    df_clean = df.dropna(subset=['true_labels', 'pred_labels'])
    
    unique_labels = sorted(list(set(df_clean['true_labels'].unique()) | 
                              set(df_clean['pred_labels'].unique())))
    unique_reactions = sorted(list(set(df_clean['true_reactions'].unique()) | 
                                 set(df_clean['pred_reactions'].unique())))

    print("\nCalculating classification metrics...")
    classification_metrics = {
        'Accuracy': accuracy_score(df_clean['true_labels'], df_clean['pred_labels']),
        'Macro Precision': precision_score(df_clean['true_labels'], 
                                         df_clean['pred_labels'], 
                                         average='macro',
                                         labels=unique_labels),
        'Macro Recall': recall_score(df_clean['true_labels'], 
                                   df_clean['pred_labels'], 
                                   average='macro',
                                   labels=unique_labels),
        'Macro F1': f1_score(df_clean['true_labels'], 
                            df_clean['pred_labels'], 
                            average='macro',
                            labels=unique_labels)
    }

    print("\nCalculating reaction metrics...")
    reaction_metrics = {
        'Accuracy': accuracy_score(df_clean['true_reactions'], df_clean['pred_reactions']),
        'Macro Precision': precision_score(df_clean['true_reactions'], 
                                         df_clean['pred_reactions'], 
                                         average='macro',
                                         labels=unique_reactions),
        'Macro Recall': recall_score(df_clean['true_reactions'], 
                                   df_clean['pred_reactions'], 
                                   average='macro',
                                   labels=unique_reactions),
        'Macro F1': f1_score(df_clean['true_reactions'], 
                            df_clean['pred_reactions'], 
                            average='macro',
                            labels=unique_reactions)
    }

    # Calculate per-class metrics
    classification_class_metrics = calculate_class_metrics(df_clean['true_labels'], 
                                                         df_clean['pred_labels'], 
                                                         unique_labels)
    
    reaction_class_metrics = calculate_class_metrics(df_clean['true_reactions'], 
                                                   df_clean['pred_reactions'], 
                                                   unique_reactions)

    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f'evaluation_report_{iter}.txt'
    class_cm_filename = f'classification_confusion_matrix_{iter}.png'
    reaction_cm_filename = f'reaction_confusion_matrix_{iter}.png'

    create_confusion_matrix_class_plot(df_clean['true_labels'], 
                               df_clean['pred_labels'],
                               unique_labels,
                               class_cm_filename)
    
    create_confusion_matrix_class_plot(df_clean['true_reactions'], 
                               df_clean['pred_reactions'],
                               unique_reactions,
                               reaction_cm_filename)

    with open(report_filename, 'w') as f:
        f.write("EVALUATION REPORT\n")
        f.write("================\n\n")
        
        # Classification Metrics
        f.write("CLASSIFICATION METRICS\n")
        f.write("--------------------\n")
        f.write("Overall Metrics:\n")
        for metric, value in classification_metrics.items():
            f.write(f"{metric}: {value:.4f}\n")
        
        f.write("\nPer-Class Metrics:\n")
        for label in unique_labels:
            f.write(f"\n{label}:\n")
            for metric, value in classification_class_metrics[label].items():
                f.write(f"  {metric}: {value:.4f}\n")
        
        # Reaction Metrics
        f.write("\nREACTION METRICS\n")
        f.write("---------------\n")
        f.write("Overall Metrics:\n")
        for metric, value in reaction_metrics.items():
            f.write(f"{metric}: {value:.4f}\n")
        
        f.write("\nPer-Class Metrics:\n")
        for reaction in unique_reactions:
            f.write(f"\n{reaction}:\n")
            for metric, value in reaction_class_metrics[reaction].items():
                f.write(f"  {metric}: {value:.4f}\n")
        
        # Dataset Statistics
        f.write("\nDATASET STATISTICS\n")
        f.write("-----------------\n")
        f.write(f"Total samples: {len(df)}\n")
        f.write(f"Valid samples: {len(df_clean)}\n")
        f.write(f"Missing labels: {len(df) - len(df_clean)}\n")
        
        f.write("\nClassification distribution:\n")
        for label in unique_labels:
            true_count = sum(df_clean['true_labels'] == label)
            pred_count = sum(df_clean['pred_labels'] == label)
            correct_count = sum((df_clean['true_labels'] == label) & (df_clean['pred_labels'] == label))
            
            f.write(f"{label}:\n")
            f.write(f"  True labels: {true_count}\n")
            f.write(f"  Predicted labels: {pred_count}\n")
            f.write(f"  Correctly classified: {correct_count}\n")
            f.write(f"  Incorrectly classified: {true_count - correct_count}\n")
            
        f.write("\nReaction distribution:\n")
        for reaction in unique_reactions:
            true_count = sum(df_clean['true_reactions'] == reaction)
            pred_count = sum(df_clean['pred_reactions'] == reaction)
            correct_count = sum((df_clean['true_reactions'] == reaction) & (df_clean['pred_reactions'] == reaction))
            
            f.write(f"{reaction}:\n")
            f.write(f"  True reactions: {true_count}\n")
            f.write(f"  Predicted reactions: {pred_count}\n")
            f.write(f"  Correctly classified: {correct_count}\n")
            f.write(f"  Incorrectly classified: {true_count - correct_count}\n")

    print("\nRisultati salvati:")
    print(f"- Report: {report_filename}")
    print(f"- Classification Confusion Matrix: {class_cm_filename}")
    print(f"- Reaction Confusion Matrix: {reaction_cm_filename}")
    
    print("\nClassification metrics summary:")
    for metric, value in classification_metrics.items():
        print(f"{metric}: {value:.4f}")
        
    print("\nReaction metrics summary:")
    for metric, value in reaction_metrics.items():
        print(f"{metric}: {value:.4f}")

if __name__ == "__main__":
    main('I')
    main('II')
    main('III')
    main('IV')
    main('V')
    
    average_timing = sum(all_timings) / len(all_timings)
    print(f"TOTAL AVERAGE 'timing': {average_timing}")