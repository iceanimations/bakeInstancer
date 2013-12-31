''' 
@file bake_particle_instancer.py

This file contains functions to bake an instancer into a structure of
transforms containing instances
'''
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaFX as omfx


def get_mobjs(string, mobjs=False, dagpaths=True, plugs=False, list_all=False):
    ''' return mobjs or dagpaths or plugs that match the given string '''
    #initalize the variables
    result = []
    sel_list = om.MSelectionList()
    sel_list.add(string)
    for i in range(sel_list.length()):
        mobj, dp, plug = om.MObject(), om.MDagPath(), om.MPlug()
        obj_list = []

        if mobjs:
            try:
                sel_list.getDependNode(i, mobj)
            except RuntimeError:
                mobj = None
            finally:
                obj_list.append(mobj)

        if dagpaths:
            try:
                sel_list.getDagPath(i, dp)
            except RuntimeError:
                dp = None
            finally:
                obj_list.append(dp)

        if plugs:
            try:
                sel_list.getComponent(i, plug)
            except RuntimeError:
                plug = None
            finally:
                obj_list.append(plug)

        if len(obj_list) == 1:
            obj_list = obj_list[0]

        if not list_all:
            return obj_list
        else:
            result.append(tuple(obj_list))

    return result


def get_playback_range():
    ''' get the current playback range in maya '''
    start = mc.playbackOptions(q=1, min=1)
    end = mc.playbackOptions(q=1, max=1)
    return start, end+1


def get_inst_main_grp(inst):
    ''' given the name of the instancer get an appropriate group to contain
    the baked structure '''
    main_grp = '|' + inst + '_bakedGrp'
    if (not mc.objExists(main_grp)) or mc.nodeType(main_grp) != 'transform':
        return mc.createNode('transform', n=main_grp)
    return main_grp


def get_particle_grp(inst_main_grp, pid):
    ''' Given the particle id and the main bake grp, get the appropriate
    transform node to hold all the instances under a particle '''
    particle_grp = 'particle_' + str(int(pid)) + '_Grp'
    particle_grp_fp = '|' + inst_main_grp + '|' + particle_grp
    if ((not mc.objExists(particle_grp_fp)) or mc.nodeType(particle_grp_fp) != 'transform'):
        return mc.createNode('transform', n=particle_grp, p=inst_main_grp)
    return particle_grp_fp


def get_particle_inst_grp(particle_group, dp):
    ''' given a particle grp get an appropriate group to instance the given
    instanceable under '''
    dpa = om.MDagPathArray()
    dp.getAllPathsTo(dp.node(), dpa)
    allpaths = [dpa[i].fullPathName() for i in range(dpa.length())]
    children = mc.listRelatives(particle_group, c=1, type='transform', f=1)
    if not children:
        children = []
    for c in children:
        shapes = mc.listRelatives(c, c=1, s=1, f=1)
        if not shapes:
            shapes = []
        for s in shapes:
            dps = get_mobjs(s)
            n = dps.instanceNumber()
            if n < len(allpaths) and allpaths[n] == s:
                return c
    dup = mc.instance(dp.fullPathName())[0]
    dup = mc.parent(dup, particle_group, r=1)[0]
    return dup


def bake_particle_inst(inst):
    ''' given the name of the instancer run the time line to gather the
    information about the instancer and then create the structure for it '''
    if not mc.objExists(inst):
        mc.error("Object %s does not exist" % inst)
    if mc.nodeType(inst) != 'instancer':
        mc.error("Object %s is not of type instancer" % inst)
    inst_dagpath = get_mobjs(inst)

    inst_fn = omfx.MFnInstancer(inst_dagpath)
    try:
        inst_particle = mc.listConnections(inst + '.inputPoints')[0]
    except IndexError:
        mc.error("No particle Connected to instancer %s" % inst)

    inst_main_grp = get_inst_main_grp(inst)
    old_pid_array = []
    # dictionary to store group names for particles
    pid_groups = dict()
    # dictionary to store group names for instances under particles
    pid_insts = dict()
    for i in xrange(*get_playback_range()):
        # get all instances for this instancer
        mc.currentTime(i, e=1)
        dp_array = om.MDagPathArray()
        mat_array = om.MMatrixArray()
        si_array = om.MIntArray()
        pi_array = om.MIntArray()
        inst_fn.allInstances(dp_array, mat_array, si_array, pi_array)
        rel_mat_array = [dp_array[i].inclusiveMatrix() for i in range(dp_array.length())]
        pid_array = mc.getParticleAttr(inst_particle, at='particleId', array=True)
        if not pid_array:
            pid_array = []

        for index, pid in enumerate(pid_array):
            # get all the instances for this particle
            si = si_array[index]
            try:
                ei = si_array[index+1]-1
            except IndexError:
                ei = si_array[len(si_array)-1]
            mat = mat_array[index]
            pi = pi_array[si:ei+1]
            dps = [dp_array[x] for x in pi]
            rel_mats = [rel_mat_array[x] for x in pi]

            # get group for this particle
            particle_grp = ''
            try:
                particle_grp = pid_groups[pid]
            except KeyError:
                particle_grp = get_particle_grp(inst_main_grp, pid)
                pid_groups[pid] = particle_grp

            # transform it, make it visible and set keys
            pg_dp, pg_obj = get_mobjs(particle_grp, mobjs=True)
            tfn = om.MFnTransform(pg_obj)
            tfn.set(om.MTransformationMatrix(mat))
            mc.setAttr(particle_grp + '.v', 1)
            mc.setKeyframe([particle_grp], bd=0, hi='none', cp=0, s=0)
            mc.setKeyframe([particle_grp], bd=0, hi='none', cp=0, s=0, at='shear')

            # and hide it before this frame if there was no other keys
            if not mc.keyframe(particle_grp, q=1, at='v', t=(mc.playbackOptions(q=1, ast=1), mc.currentTime(q=1)-1)):
                mc.setKeyframe([particle_grp], at='v', t=mc.currentTime(q=1)-1, v=0, hi='none', s=0)

            # and add to its children the correspoding instances
            p_inst_grps = set()
            for i, dp in enumerate( dps ):
                #mechanism to find out existing instance copies for particle
                try:
                    particle_inst_group = pid_insts[(pid, dp.fullPathName())]
                except KeyError:
                    particle_inst_group = get_particle_inst_grp(particle_grp, dp)
                    pid_insts[(pid, dp.fullPathName())] = particle_inst_group
                p_inst_grps.add(particle_inst_group)

                # transform, make visible and key the particle-instance group
                # hide before born
                if not mc.keyframe(particle_inst_group, q=1, at='v', t=(mc.playbackOptions(q=1, ast=1), mc.currentTime(q=1)-1)):
                    mc.setKeyframe([particle_inst_group], at='v', t=mc.currentTime(q=1)-1, v=0, hi='none', s=0)
                #mc.setAttr(particle_inst_group + '.v', 1)
                om.MFnTransform(get_mobjs(particle_inst_group)).set(om.MTransformationMatrix(rel_mats[i]))
                mc.setKeyframe([particle_inst_group], bd=0, hi='none', cp=0, s=0)

            # hide all other children (instances)
            children = mc.listRelatives(particle_grp, c=1, type='transform', f=1)
            if not children:
                children = []
            for c in children:
                if c not in p_inst_grps:
                    mc.setKeyframe([c], at='v', hi='none', s=0, v=0, t=mc.currentTime(q=1))

            # and make the instances visible
            if p_inst_grps:
                mc.setKeyframe(list(p_inst_grps), at='v', v=1, hi='none', s=0,
                        t=mc.currentTime(q=1))

        # hide particles that have died
        for pid in old_pid_array:
            if pid not in pid_array:
                particle_grp = pid_groups[pid]
                print "particle %i has died at t=%d: %s" % (pid, mc.currentTime(q=1), particle_grp)
                mc.setKeyframe([particle_grp], at='v', hi='none', s=0, v=0, t=mc.currentTime(q=1))
        old_pid_array = pid_array


def main():
    bake_particle_inst('instancer1')


if __name__ == '__main__':
    main()

