def caculate_hit1(prediction, ground_truth):
    prediction = [p.lower() for p in prediction]
    ground_truth = [g.lower() for g in ground_truth]
    if ground_truth == []:
        return 1
    if prediction == []:
        return 0
    else:
        if prediction[0] in ground_truth:
            return 1
    return 0
def caculate_hit(prediction, ground_truth):
    prediction = [p.lower() for p in prediction]
    ground_truth = [g.lower() for g in ground_truth]
    if ground_truth == []:
        return 1
    if prediction == []:
        return 0
    else:
        for p in prediction:
            if p in ground_truth:
                return 1
    return 0
def caculate_precision(prediction, ground_truth):
    prediction = [p.lower() for p in prediction]
    ground_truth = [g.lower() for g in ground_truth]
    if ground_truth == []:
        return 1
    if prediction == []:
        return 0
    else:
        count = 0
        for p in prediction:
            if p in ground_truth:
                count += 1
        return count / len(prediction)
def caculate_recall(prediction, ground_truth):
    prediction = [p.lower() for p in prediction]
    ground_truth = [g.lower() for g in ground_truth]
    if ground_truth == []:
        return 1
    else:
        count = 0
        for p in ground_truth:
            if p in prediction:
                count += 1
        return count / len(ground_truth)
def caculate_f1(prediction, ground_truth):
    prediction = [p.lower() for p in prediction]
    ground_truth = [g.lower() for g in ground_truth]
    if ground_truth == []:
        return 1
    precision = caculate_precision(prediction, ground_truth)
    recall = caculate_recall(prediction, ground_truth)
    if precision + recall == 0:
        return 0
    else:
        f1 = (2 * precision * recall) / (precision + recall)
        return f1