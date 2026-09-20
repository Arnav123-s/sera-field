"""Conditional trajectories from acquired coefficient hypotheses, without truth."""
import numpy as np


def rollout(coefficients, velocity, force_per_mass, duration, steps=128):
    coefficients = np.asarray(coefficients, dtype='float64')
    if coefficients.shape != (3, 4) or not np.isfinite(coefficients).all():
        raise ValueError('Three finite learned coefficient hypotheses required')
    if not np.isfinite([velocity, force_per_mass, duration]).all():
        raise ValueError('Finite initial velocity, applied force/mass and duration required')
    if not 0 < duration <= 5 or not isinstance(steps, int) or steps < 16:
        raise ValueError('Duration in (0,5] and at least 16 integration steps required')
    state = np.zeros((3, 2), dtype='float64')
    state[:, 1] = velocity
    dt = duration / steps
    def derivative(y):
        v = y[:, 1]
        acceleration = (coefficients[:, 0] * force_per_mass + coefficients[:, 1] * v
                        + coefficients[:, 2] * v * np.abs(v) + coefficients[:, 3])
        return np.column_stack((v, acceleration))
    path = [state.copy()]
    for _ in range(steps):
        a = derivative(state)
        b = derivative(state + .5 * dt * a)
        c = derivative(state + .5 * dt * b)
        d = derivative(state + dt * c)
        state += dt * (a + 2*b + 2*c + d) / 6
        if not np.isfinite(state).all() or np.max(np.abs(state)) > 10000:
            return {'status': 'diverged', 'steps_completed': len(path)-1,
                    'assumptions': 'Learned finite acceleration basis and constant applied force/mass'}
        path.append(state.copy())
    return {'status': 'completed', 'position_velocity_hypotheses': state.tolist(),
            'position_velocity_mean': state.mean(0).tolist(),
            'sampled_trajectory': np.asarray(path)[::max(1,steps//16)].tolist(),
            'duration': duration, 'integration': 'RK4 using only learned coefficients'}
