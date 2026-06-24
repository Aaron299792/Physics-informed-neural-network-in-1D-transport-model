import numpy as np
import deepxde as dde
import torch

class pinn:
    def __init__(self, input_size,
                       hidden_size,
                       output_size,
                       domain_size,
                       boundary_size,
                       test_size,
                       iter_pre,
                       iter_size,
                       solution = None
                       ):

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.domain_size = domain_size
        self.boundary_size = boundary_size
        self.test_size = test_size
        self.iter_pre = iter_pre
        self.iter_size = iter_size
        self.solution = solution

    def sol(self, ode_func, geom, boundaries, x_eval, weights=None, refinement=False):
        num_layers = int(len(boundaries) + self.output_size)
        data = dde.data.PDE(geom, ode_func, boundaries, self.domain_size,
                            self.boundary_size, num_test = self.test_size, solution=self.solution)

        net = dde.nn.FNN([self.input_size] + [self.hidden_size] * num_layers + [self.output_size],
                          "tanh", "Glorot normal")

        net.apply_output_transform(lambda x, y: torch.exp(y) / (1 + torch.exp(y)))

        model = dde.Model(data, net)

        model.compile("adam", lr=1e-3, loss_weights=weights)
        model.train(iterations=self.iter_pre, verbose=0)

        model.compile("adam", lr=1e-4, loss_weights=weights)
        model.train(iterations=self.iter_size, verbose=0)


        if (refinement == True):
            dde.optimizers.config.set_LBFGS_options(maxiter=2000,
                                                    maxfun=2500,
                                                    ftol=1e-9,
                                                    gtol=1e-7)
            model.compile("L-BFGS", )
            model.train(verbose=0)
        return model.predict(x_eval), model.predict(x_eval, operator = ode_func)
