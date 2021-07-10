import tensorflow as tf

sess = tf.Session()
new_saver = tf.train.import_meta_graph('/home/cwang717/tensorflow/model.meta')
new_saver.restore(sess, tf.train.latest_checkpoint('/home/cwang717/tensorflow/'))


obs = sess.graph.get_tensor_by_name("default_policy/observation:0")
nodes = [n.name for n in tf.get_default_graph().as_graph_def().node]

def compute_tensor(node):
    try:
        return sess.run(sess.graph.get_tensor_by_name(node+":0"), {obs:[[0.22134309, 0.00360639, 0.06868469]]})
    except:
        return None

results = {}
for node in nodes:
    results[node] = compute_tensor(node)

print(results)

sess.close()