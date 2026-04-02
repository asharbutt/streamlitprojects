import numpy as np
import plotly.graph_objects as go

import numpy as np
import plotly.graph_objects as go
class binomial_tree_vanilla:

    def __init__(self, steps, vol, spot, strike, t,option_type, r,exercise_type):
        self.steps = steps+1 # We start off at 0,0 and then have x additional steps from that
        self.exercise_type = exercise_type
        self.initial_spot = spot
        self.time_step = t / steps
        self.strike = strike
        self.asset_matrix = np.zeros((self.steps,self.steps))
        self.option_matrix = np.zeros((self.steps,self.steps))
        if option_type=='call': self.option_flag = 1
        else: self.option_flag = -1
        self.up = np.exp(vol*np.sqrt(self.time_step))
        self.down = pow(self.up,-1)
        self.probability = (np.exp(r*self.time_step)-self.down)/(self.up - self.down)
        self.discount_factor = np.exp(-r*self.time_step)

    def compute_european_option(self):
        # Now we calculate the option value, starting off from the end and working backwards:
        self.option_matrix[:,-1] = np.maximum(self.option_flag*(self.asset_matrix[:,-1]-self.strike),0)

        for j in range(self.steps-2, 0, -1):
            for i in range(0, self.steps-1):
                if i > j:
                    break
                self.option_matrix[i,j] = self.discount_factor * (self.option_matrix[i,j+1] * self.probability + self.option_matrix[i+1,j+1] * (1 - self.probability))

        self.option_matrix[0, 0] = self.discount_factor * (self.option_matrix[0,  1] * self.probability + self.option_matrix[1, 1] * (1 - self.probability))

        print(self.option_matrix)
        return self.option_matrix[0, 0]

    def compute_american_option(self):
        # Now we calculate the option value, starting off from the end and working backwards:
        self.option_matrix[:,-1] = np.maximum(self.option_flag*(self.asset_matrix[:,-1]-self.strike),0)

        for j in range(self.steps-2, 0, -1):
            for i in range(0, self.steps-1):
                if i > j:
                    break
                self.option_matrix[i,j] = np.maximum(self.discount_factor * (self.option_matrix[i,j+1] * self.probability + self.option_matrix[i+1,j+1] * (1 - self.probability)), self.option_flag*(self.asset_matrix[i,j]-self.strike))

        self.option_matrix[0, 0] = np.maximum(self.discount_factor * (self.option_matrix[0,  1] * self.probability + self.option_matrix[1, 1] * (1 - self.probability)),self.option_flag*(self.asset_matrix[0,0]-self.strike))

        print(self.option_matrix)
        return self.option_matrix[0, 0]

    def run_tree(self):
        # Compute the asset matrix first:
        self.asset_matrix[0,0] = self.initial_spot
        print(self.probability)

        for j in range(1, self.steps):
            for i in range(0,self.steps):
                if i == 0:
                        self.asset_matrix[i,j] = self.asset_matrix[i,j-1]*self.up
                else:
                    self.asset_matrix[i,j] = self.asset_matrix[i-1,j-1]*self.down

        print("Asset Matrix: ")
        print(self.asset_matrix)

        if self.exercise_type == 'european': option_price = self.compute_european_option()
        elif self.exercise_type == 'american':  option_price = self.compute_american_option()

        return option_price


def plot_binomial_tree(tree: binomial_tree_vanilla):
    node_x, node_y, node_text = [], [], []
    edge_x, edge_y = [], []

    for j in range(tree.steps):  # 0 to steps-1 (all columns)
        for i in range(j + 1):  # 0 to j (nodes at this step)
            price = tree.asset_matrix[i, j]
            node_x.append(j)  # x = time step (not i)
            node_y.append(price)
            node_text.append(f"S={price:.2f}<br>V={tree.option_matrix[i, j]:.2f}")

            if j < tree.steps - 1:  # don't look ahead from last column
                next_up = tree.asset_matrix[i, j + 1]
                next_down = tree.asset_matrix[i + 1, j + 1]
                for next_price in [next_up, next_down]:
                    edge_x += [j, j + 1, None]
                    edge_y += [price, next_price, None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines',line=dict(color='gray', width=1), hoverinfo='none'))
    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers+text',marker=dict(size=50, color='royalblue'),text=node_text, textposition='middle center',textfont=dict(size=12, color='white')))
    fig.update_layout(template='plotly_dark', showlegend=False)
    return fig
